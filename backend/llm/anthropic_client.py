import os

import anthropic
from pydantic import BaseModel

# Low temperature by default everywhere in this app: for factual Q&A over a
# legal document, faithfulness matters far more than varied/creative phrasing.
DEFAULT_TEMPERATURE = 0.0


def get_client() -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def get_model() -> str:
    return os.getenv("ANTHROPIC_CHAT_MODEL", "claude-sonnet-4-5")


def get_structured_completion(
    prompt: str,
    response_model: type[BaseModel],
    system: str = "You are a meticulous privacy-policy analyst.",
) -> BaseModel:
    """Get a response constrained to a Pydantic schema.

    Anthropic has no `response_format=` parse mode, so this forces the model
    to call a single synthetic tool whose input schema is the Pydantic
    model's JSON schema, then validates the tool call's input against it.
    """
    client = get_client()
    schema = response_model.model_json_schema()

    response = client.messages.create(
        model=get_model(),
        max_tokens=2048,
        temperature=DEFAULT_TEMPERATURE,
        system=system,
        messages=[{"role": "user", "content": prompt}],
        tools=[
            {
                "name": "record_extraction",
                "description": "Record the extracted structured data.",
                "input_schema": schema,
            }
        ],
        tool_choice={"type": "tool", "name": "record_extraction"},
    )

    for block in response.content:
        if block.type == "tool_use" and block.name == "record_extraction":
            return response_model.model_validate(block.input)

    raise RuntimeError("Model did not return a structured tool call.")


def get_chat_completion(
    system: str,
    user_message: str,
    temperature: float = DEFAULT_TEMPERATURE,
) -> str:
    """Plain grounded chat completion (no structured output)."""
    client = get_client()

    response = client.messages.create(
        model=get_model(),
        max_tokens=1024,
        temperature=temperature,
        system=system,
        messages=[{"role": "user", "content": user_message}],
    )

    return "".join(block.text for block in response.content if block.type == "text")

from pydantic import BaseModel, Field

from embeddings.openai_embeddings import get_embeddings
from llm.anthropic_client import get_structured_completion
from vectorstore.pgvector_store import Retriever


class ExtractedAttributes(BaseModel):
    effective_date: str | None = Field(None, description="Policy's effective/last-updated date, if stated")
    data_collected: list[str] | None = Field(None, description="Categories of personal data collected")
    shares_with_third_parties: bool | None = Field(None, description="Whether data is shared with third parties")
    third_parties_named: list[str] | None = Field(None, description="Specific third parties/categories named")
    sells_data: bool | None = Field(None, description="Whether the policy states data is sold")
    retention_period: str | None = Field(None, description="How long data is retained")
    user_rights: list[str] | None = Field(None, description="Rights offered: access, deletion, opt-out, portability, etc.")
    uses_cookies_tracking: bool | None = Field(None, description="Whether cookies/tracking technologies are used")
    children_data_collected: bool | None = Field(None, description="Whether the policy addresses children's data (COPPA)")
    gdpr_mentioned: bool | None = Field(None, description="Whether GDPR is referenced")
    ccpa_mentioned: bool | None = Field(None, description="Whether CCPA/CPRA is referenced")
    breach_notification: str | None = Field(None, description="Data breach notification commitment, if any")
    international_transfer: str | None = Field(None, description="International data transfer disclosure, if any")
    contact_email: str | None = Field(None, description="Privacy contact email, if listed")
    risk_flags: list[str] | None = Field(
        None,
        description="Concise, concrete red flags for a privacy-conscious user (e.g. broad data-sharing language, no deletion right, indefinite retention)",
    )
    summary: str | None = Field(None, description="2-3 sentence plain-English summary of the policy")


def retrieve_broad_context(company: str, workspace_id: str, top_k: int = 30) -> str:
    """Pull a broad sample of a company's chunks to ground attribute extraction."""
    retriever = Retriever()
    embeddings = get_embeddings()

    query = (
        "data collection, data sharing, third parties, data retention, "
        "user rights, cookies and tracking, children's privacy, "
        "GDPR, CCPA, data breach notification, international transfer, contact information"
    )

    chunks = retriever.invoke(query=query, embeddings=embeddings, workspace_id=workspace_id, company=company, top_k=top_k)

    return "\n\n".join(chunk.content for chunk in chunks)


def build_extraction_prompt(company: str, context: str) -> str:
    return f"""
Company: {company}

Below are passages retrieved from {company}'s privacy policy:

{context}

Extract the requested privacy-policy attributes using ONLY the passages above.

Instructions:
- If a fact is not stated in the passages, return null for that field — do not guess or infer from general knowledge of the company.
- Boolean fields must reflect only what is explicitly stated.
- risk_flags should be concrete and specific to this policy's actual language, not generic warnings.
- summary must be plain English, understandable to someone with no legal background.
"""


def extract_attributes(company: str, workspace_id: str) -> dict:
    context = retrieve_broad_context(company, workspace_id=workspace_id)

    if not context.strip():
        raise ValueError(f"No ingested content found for company={company!r}")

    prompt = build_extraction_prompt(company, context)

    result = get_structured_completion(
        prompt=prompt,
        response_model=ExtractedAttributes,
        system="You are a meticulous privacy-policy analyst. You never state a fact that isn't backed by the provided passages.",
    )

    return result.model_dump()

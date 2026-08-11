from sqlalchemy import text

from database.db import get_engine, get_session
from database.models import ChatLog, PrivacyAttributes


def save_attributes(company: str, source: str, attributes: dict) -> None:
    """Persist extracted privacy attributes for one ingested policy."""
    session = get_session()

    try:
        row = PrivacyAttributes(company=company, source=source, **attributes)
        session.add(row)
        session.commit()
        print(f"Saved privacy attributes for {company} ({source})")
    finally:
        session.close()


def get_latest_attributes() -> list[dict]:
    """Return the most recently ingested attributes per company, for the dashboard."""
    engine = get_engine()

    query = """
    SELECT *
    FROM (
        SELECT *,
               ROW_NUMBER() OVER (
                   PARTITION BY company
                   ORDER BY created_at DESC
               ) AS rn
        FROM privacy_attributes
    ) t
    WHERE rn = 1
    ORDER BY company
    """

    with engine.connect() as connection:
        result = connection.execute(text(query))
        return [dict(row._mapping) for row in result]


def save_chat_log(
    company: str | None,
    question: str,
    answer: str,
    retrieved_chunk_ids: list[str],
    top_similarity: float | None,
    was_insufficient_context: bool,
) -> None:
    """Log a chat exchange for the offline faithfulness-sampling / human-labeling layers."""
    session = get_session()

    try:
        row = ChatLog(
            company=company,
            question=question,
            answer=answer,
            retrieved_chunk_ids=retrieved_chunk_ids,
            top_similarity=top_similarity,
            was_insufficient_context=was_insufficient_context,
        )
        session.add(row)
        session.commit()
    finally:
        session.close()

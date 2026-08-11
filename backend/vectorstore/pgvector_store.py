from dataclasses import dataclass

from database.db import get_session
from database.models import PolicyChunk


def upload_chunks(chunks, embeddings, company: str, source: str) -> None:
    """Embed and store a document's chunks in Postgres/pgvector."""
    session = get_session()

    try:
        texts = [chunk.page_content for chunk in chunks]
        vectors = embeddings.embed_documents(texts)

        for chunk, vector in zip(chunks, vectors):
            row = PolicyChunk(
                company=company,
                source=source,
                content=chunk.page_content,
                embedding=vector,
            )
            session.add(row)

        session.commit()
        print(f"Uploaded {len(chunks)} chunks for {company} ({source}).")
    finally:
        session.close()


@dataclass
class RetrievedChunk:
    id: str
    content: str
    source: str
    similarity: float


class Retriever:
    """Vector similarity search over policy_chunks, filterable by company."""

    def invoke(
        self,
        query: str,
        embeddings,
        company: str | None = None,
        top_k: int = 8,
    ) -> list[RetrievedChunk]:
        session = get_session()

        try:
            query_vector = embeddings.embed_query(query)

            # cosine_distance ranges 0 (identical) .. 2 (opposite);
            # similarity = 1 - distance gives the more intuitive 0..1 scale
            # used for the confidence threshold in rag/chat.py.
            distance_expr = PolicyChunk.embedding.cosine_distance(query_vector)

            statement = session.query(
                PolicyChunk.id,
                PolicyChunk.content,
                PolicyChunk.source,
                distance_expr.label("distance"),
            )

            if company:
                statement = statement.filter(PolicyChunk.company == company)

            statement = statement.order_by(distance_expr).limit(top_k)

            results = []
            for chunk_id, content, source, distance in statement.all():
                results.append(
                    RetrievedChunk(
                        id=str(chunk_id),
                        content=content,
                        source=source,
                        similarity=1 - float(distance),
                    )
                )

            return results
        finally:
            session.close()

from sqlalchemy import text

from database.db import get_engine
from database.models import Base


def create_tables() -> None:
    engine = get_engine()

    with engine.begin() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))

    Base.metadata.create_all(engine)

    with engine.begin() as connection:
        connection.execute(
            text(
                """
                CREATE INDEX IF NOT EXISTS policy_chunks_embedding_idx
                ON policy_chunks USING hnsw (embedding vector_cosine_ops)
                """
            )
        )

    print("Tables and pgvector index ready.")


if __name__ == "__main__":
    from database.db import create_database

    create_database()
    create_tables()

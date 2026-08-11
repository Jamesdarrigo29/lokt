import os

import psycopg
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

_engine = None
_SessionLocal = None


def get_connection_params() -> dict:
    return {
        "host": os.getenv("POSTGRES_HOST"),
        "port": os.getenv("POSTGRES_PORT"),
        "user": os.getenv("POSTGRES_USER"),
        "password": os.getenv("POSTGRES_PASSWORD"),
        "database": os.getenv("POSTGRES_DATABASE"),
    }


def get_engine():
    """Create (once) and return the SQLAlchemy engine."""
    global _engine

    if _engine is None:
        params = get_connection_params()

        connection_string = (
            f"postgresql+psycopg://{params['user']}:{params['password']}"
            f"@{params['host']}:{params['port']}/{params['database']}"
        )

        _engine = create_engine(connection_string)

    return _engine


def get_session():
    global _SessionLocal

    if _SessionLocal is None:
        _SessionLocal = sessionmaker(bind=get_engine())

    return _SessionLocal()


def create_database() -> None:
    """Create the target database if it does not exist yet."""
    params = get_connection_params()

    conn = psycopg.connect(
        host=params["host"],
        port=params["port"],
        dbname="postgres",
        user=params["user"],
        password=params["password"],
        autocommit=True,
    )

    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (params["database"],),
        )

        if not cursor.fetchone():
            print(f"Database '{params['database']}' does not exist. Creating...")
            cursor.execute(f"CREATE DATABASE {params['database']}")
        else:
            print(f"Database '{params['database']}' already exists.")
    finally:
        cursor.close()
        conn.close()

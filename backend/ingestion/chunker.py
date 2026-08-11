from pathlib import Path

from langchain_core.documents import Document
from langchain_experimental.text_splitter import SemanticChunker


def read_markdown(markdown_file: str) -> str:
    return Path(markdown_file).read_text(encoding="utf-8")


def chunk_markdown(markdown_file: str, embeddings) -> list[Document]:
    """Split a policy's markdown into semantically-coherent chunks.

    Splitting on detected topic shifts (rather than fixed character counts)
    keeps each chunk focused on one clause/topic, which matters for both
    retrieval precision and citation quality.
    """
    markdown_content = read_markdown(markdown_file)

    splitter = SemanticChunker(
        embeddings=embeddings,
        breakpoint_threshold_type="percentile",
    )

    return splitter.create_documents([markdown_content])

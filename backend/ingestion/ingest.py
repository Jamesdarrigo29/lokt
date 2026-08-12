from ingestion.chunker import chunk_markdown
from ingestion.pdf_to_markdown import convert_pdf
from ingestion.url_to_markdown import convert_url
from embeddings.openai_embeddings import get_embeddings
from vectorstore.pgvector_store import upload_chunks
from rag.attribute_extractor import extract_attributes
from database.queries import save_attributes


def ingest_pdf(pdf_path: str, company: str, source_label: str, workspace_id: str) -> dict:
    markdown_file = convert_pdf(pdf_path=pdf_path, output_dir="data/markdown")
    return _ingest_markdown(markdown_file, company=company, source_label=source_label, workspace_id=workspace_id)


def ingest_url(url: str, company: str, workspace_id: str) -> dict:
    markdown_file = convert_url(url=url, output_dir="data/markdown")
    return _ingest_markdown(markdown_file, company=company, source_label=url, workspace_id=workspace_id)


def _ingest_markdown(markdown_file: str, company: str, source_label: str, workspace_id: str) -> dict:
    embeddings = get_embeddings()

    chunks = chunk_markdown(markdown_file=markdown_file, embeddings=embeddings)
    print(f"Generated {len(chunks)} chunks for {company} ({source_label})")

    upload_chunks(
        chunks=chunks, embeddings=embeddings, workspace_id=workspace_id, company=company, source=source_label
    )

    attributes = extract_attributes(company=company, workspace_id=workspace_id)
    save_attributes(workspace_id=workspace_id, company=company, source=source_label, attributes=attributes)

    return {"company": company, "source": source_label, "chunks": len(chunks), "attributes": attributes}

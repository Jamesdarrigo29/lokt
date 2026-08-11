from pathlib import Path

import pymupdf4llm


def convert_pdf(pdf_path: str, output_dir: str) -> str:
    """Convert a PDF privacy policy to Markdown. Returns the markdown file path."""
    pdf_file = Path(pdf_path)

    if not pdf_file.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    markdown_content = pymupdf4llm.to_markdown(str(pdf_file))

    markdown_file = output_path / f"{pdf_file.stem}.md"
    markdown_file.write_text(markdown_content, encoding="utf-8")

    return str(markdown_file)

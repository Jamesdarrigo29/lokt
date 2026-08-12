import shutil
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool

from ingestion.ingest import ingest_pdf, ingest_url
from ratelimit import limiter

router = APIRouter()


@router.post("/upload")
@limiter.limit("10/hour")
async def upload_document(request: Request, company: str, file: UploadFile = File(...)):
    upload_dir = Path("data/raw_pdfs")
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_path = upload_dir / file.filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # Ingestion (chunking, embeddings, LLM calls, and now Playwright for
        # JS-rendered pages) is synchronous, blocking work — run it in a
        # worker thread rather than the event-loop thread. This isn't just a
        # performance nicety: Playwright's sync API actively refuses to run
        # inside a thread that already has a running asyncio event loop,
        # which every FastAPI request handler's thread does.
        result = await run_in_threadpool(
            ingest_pdf,
            pdf_path=str(file_path),
            company=company,
            source_label=file.filename,
            workspace_id=request.state.workspace_id,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {"message": "Document ingested successfully", **result}


class AnalyzeUrlRequest(BaseModel):
    company: str
    url: str


@router.post("/analyze-url")
@limiter.limit("10/hour")
async def analyze_url(request: Request, body: AnalyzeUrlRequest):
    try:
        result = await run_in_threadpool(
            ingest_url, url=body.url, company=body.company, workspace_id=request.state.workspace_id
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {"message": "Page ingested successfully", **result}

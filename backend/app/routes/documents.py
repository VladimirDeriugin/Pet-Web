"""Document analysis API routes."""

import logging
from fastapi import APIRouter, File, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse

from app.models.document import AnalysisResult, DocumentStats, KeywordItem, NamedEntity
from app.services.document_parser import extract_text
from app.services.ml_analyzer import analyze_document

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/documents", tags=["documents"])

_MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post(
    "/analyze",
    response_model=AnalysisResult,
    status_code=status.HTTP_200_OK,
    summary="Upload and analyse a document",
    description=(
        "Upload a PDF, DOCX, or TXT file. "
        "Returns statistics, keywords, summary, sentiment, entities and language."
    ),
)
async def analyze_document_endpoint(
    file: UploadFile = File(..., description="PDF, DOCX or TXT document"),
) -> AnalysisResult:
    if file.filename is None or file.filename == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided.",
        )

    content = await file.read()
    if len(content) > _MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds the {_MAX_FILE_SIZE // (1024 * 1024)} MB size limit.",
        )
    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    try:
        text, file_type = extract_text(file.filename, content)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=str(exc),
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    if not text.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No extractable text found in the document.",
        )

    analysis = analyze_document(text)

    return AnalysisResult(
        filename=file.filename,
        file_type=file_type,
        language=analysis["language"],
        stats=DocumentStats(
            word_count=analysis["word_count"],
            sentence_count=analysis["sentence_count"],
            paragraph_count=analysis["paragraph_count"],
            character_count=analysis["character_count"],
            reading_time_minutes=analysis["reading_time_minutes"],
        ),
        keywords=[KeywordItem(**kw) for kw in analysis["keywords"]],
        summary=analysis["summary"],
        sentiment=analysis["sentiment"],
        sentiment_score=analysis["sentiment_score"],
        entities=[NamedEntity(**e) for e in analysis["entities"]],
        full_text=text[:2000] if text else None,
    )


@router.get(
    "/health",
    summary="Health check",
    description="Returns the service health status.",
)
async def health() -> JSONResponse:
    return JSONResponse({"status": "ok"})

"""Document text-extraction service.

Supports PDF, DOCX and plain-text uploads.
"""

import io
import logging
from pathlib import Path
from typing import Tuple

logger = logging.getLogger(__name__)

_SUPPORTED = {".pdf", ".docx", ".doc", ".txt", ".md"}


def extract_text(filename: str, content: bytes) -> Tuple[str, str]:
    """Return *(extracted_text, file_type)* for the uploaded file bytes.

    Parameters
    ----------
    filename:
        Original filename including extension.
    content:
        Raw bytes of the uploaded file.

    Raises
    ------
    ValueError
        When the file extension is not supported.
    RuntimeError
        When parsing fails.
    """
    suffix = Path(filename).suffix.lower()
    if suffix not in _SUPPORTED:
        raise ValueError(
            f"Unsupported file type '{suffix}'. "
            f"Supported types: {', '.join(sorted(_SUPPORTED))}"
        )

    if suffix == ".pdf":
        return _extract_pdf(content), "PDF"
    if suffix in {".docx", ".doc"}:
        return _extract_docx(content), "DOCX"
    # plain text / markdown
    return _extract_text(content), "TXT"


def _extract_pdf(content: bytes) -> str:
    try:
        import PyPDF2  # noqa: PLC0415

        reader = PyPDF2.PdfReader(io.BytesIO(content))
        pages: list[str] = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
        return "\n\n".join(pages)
    except Exception as exc:
        logger.exception("PDF extraction failed")
        raise RuntimeError(f"PDF extraction failed: {exc}") from exc


def _extract_docx(content: bytes) -> str:
    try:
        import docx  # noqa: PLC0415

        doc = docx.Document(io.BytesIO(content))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n\n".join(paragraphs)
    except Exception as exc:
        logger.exception("DOCX extraction failed")
        raise RuntimeError(f"DOCX extraction failed: {exc}") from exc


def _extract_text(content: bytes) -> str:
    for encoding in ("utf-8", "latin-1", "cp1252"):
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise RuntimeError("Unable to decode text file with supported encodings.")

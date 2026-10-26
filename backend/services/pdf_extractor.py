"""
PDF text extraction using PyMuPDF with automatic OCR fallback for scanned pages.
Also supports converting image files (PNG, JPG, JPEG, TIFF, WEBP, BMP) into
a single-page PDF before running the standard extraction + OCR pipeline.
Returns a list of PageContent objects, one per extractable page.
"""
from __future__ import annotations
import logging
import os
import urllib.request
from pathlib import Path
from typing import NamedTuple

from config import settings

logger = logging.getLogger(__name__)

# Ensure TESSDATA_PREFIX is set before importing fitz
if settings.TESSDATA_DIR.exists():
    os.environ["TESSDATA_PREFIX"] = str(settings.TESSDATA_DIR.resolve())


class PageContent(NamedTuple):
    page: int          # 1-indexed
    text: str
    is_ocr: bool = False


class ExtractionResult(NamedTuple):
    pages: list[PageContent]
    page_count: int
    total_chars: int
    ocr_applied: bool
    scanned_pages: list[int]
    error: str | None


# File extensions that are treated as images and auto-converted to PDF
SUPPORTED_IMAGE_EXTENSIONS: frozenset[str] = frozenset(
    {".png", ".jpg", ".jpeg", ".tiff", ".tif", ".webp", ".bmp"}
)


def image_to_pdf(image_path: Path) -> bytes:
    """
    Convert a single image file to PDF bytes using PyMuPDF.

    PyMuPDF can open PNG, JPG, JPEG, TIFF, WEBP, BMP natively.
    The returned bytes are a valid, single-page PDF that can be
    written to disk and fed into `extract_text()`.

    Raises:
        ImportError: if PyMuPDF is not installed.
        ValueError: if the image cannot be opened or converted.
    """
    try:
        import fitz  # PyMuPDF
    except ImportError:
        raise ImportError("PyMuPDF (fitz) is not installed.")

    try:
        # Open the raw image with PyMuPDF
        img_doc = fitz.open(str(image_path))
        # convert_to_pdf() returns bytes of a PDF where each image is one page
        pdf_bytes: bytes = img_doc.convert_to_pdf()
        img_doc.close()
        if not pdf_bytes:
            raise ValueError("convert_to_pdf() returned empty bytes.")
        return pdf_bytes
    except Exception as exc:
        raise ValueError(f"Failed to convert image to PDF: {exc}") from exc


def _clean_text(raw_text: str) -> str:
    """Normalize whitespace and remove zero-width / strange unicode characters."""
    if not raw_text:
        return ""
    return (
        raw_text.replace("\xa0", " ")
        .replace("\u202f", " ")
        .replace("\u2007", " ")
        .replace("\u200b", "")
        .strip()
    )


def ensure_tessdata() -> bool:
    """
    Ensure the eng.traineddata file is present in settings.TESSDATA_DIR.
    Downloads it from official tessdata_fast if missing.
    """
    try:
        settings.TESSDATA_DIR.mkdir(parents=True, exist_ok=True)
        eng_file = settings.TESSDATA_DIR / "eng.traineddata"
        if not eng_file.exists() or eng_file.stat().st_size == 0:
            logger.info("Downloading eng.traineddata for OCR support...")
            url = "https://github.com/tesseract-ocr/tessdata_fast/raw/main/eng.traineddata"
            urllib.request.urlretrieve(url, str(eng_file))
            logger.info("Successfully downloaded eng.traineddata.")
        return eng_file.exists() and eng_file.stat().st_size > 0
    except Exception as exc:
        logger.warning(f"Could not prepare tessdata for OCR: {exc}")
        return False


def extract_text(pdf_path: Path) -> ExtractionResult:
    """
    Extract text from a PDF file page-by-page.
    Automatically applies OCR when a page has no selectable text (scanned image).

    Returns an ExtractionResult. On failure, .error is set and .pages is empty.
    """
    try:
        import fitz  # PyMuPDF
    except ImportError:
        return ExtractionResult([], 0, 0, False, [], "PyMuPDF (fitz) is not installed.")

    try:
        doc = fitz.open(str(pdf_path))
    except Exception as exc:
        return ExtractionResult([], 0, 0, False, [], f"Failed to open PDF: {exc}")

    pages: list[PageContent] = []
    scanned_pages: list[int] = []

    # Verify or initialize OCR capability if enabled
    ocr_ready = False
    if settings.OCR_ENABLED:
        ocr_ready = ensure_tessdata()

    for page_num in range(len(doc)):
        try:
            page = doc.load_page(page_num)
            raw_text = page.get_text("text")
            cleaned_text = _clean_text(raw_text)

            # Check if this page appears to be a scanned page or has minimal text
            # (less than 30 characters of readable text)
            needs_ocr = len(cleaned_text) < 30

            if needs_ocr and settings.OCR_ENABLED and ocr_ready:
                try:
                    # Run PyMuPDF's built-in Tesseract OCR over the page
                    textpage_ocr = page.get_textpage_ocr(
                        language="eng",
                        dpi=settings.OCR_DPI,
                        full=True,
                        tessdata=str(settings.TESSDATA_DIR.resolve()),
                    )
                    ocr_raw = page.get_text("text", textpage=textpage_ocr)
                    ocr_cleaned = _clean_text(ocr_raw)

                    # If OCR yielded meaningful text exceeding standard extraction, use it
                    if len(ocr_cleaned) > len(cleaned_text):
                        pages.append(PageContent(page=page_num + 1, text=ocr_cleaned, is_ocr=True))
                        scanned_pages.append(page_num + 1)
                        continue
                except Exception as ocr_err:
                    logger.warning(f"OCR failed on page {page_num + 1}: {ocr_err}")

            # Fallback to standard cleaned text if available
            if cleaned_text:
                pages.append(PageContent(page=page_num + 1, text=cleaned_text, is_ocr=False))

        except Exception as page_err:
            logger.warning(f"Error reading page {page_num + 1}: {page_err}")
            continue  # skip unreadable pages, continue with rest

    page_count = len(doc)
    doc.close()

    total_chars = sum(len(p.text) for p in pages)
    ocr_applied = len(scanned_pages) > 0

    if not pages:
        return ExtractionResult(
            pages=[],
            page_count=page_count,
            total_chars=0,
            ocr_applied=False,
            scanned_pages=[],
            error="No extractable text found in this PDF even after OCR analysis.",
        )

    return ExtractionResult(
        pages=pages,
        page_count=page_count,
        total_chars=total_chars,
        ocr_applied=ocr_applied,
        scanned_pages=scanned_pages,
        error=None,
    )

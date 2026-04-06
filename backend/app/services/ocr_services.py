import fitz
import pytesseract
from PIL import Image
import io
import re
from dateutil import parser as date_parser

from app.config import TESSERACT_CMD

pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD


def _extract_text_from_image(image_path: str) -> str:
    image = Image.open(image_path)
    return pytesseract.image_to_string(image)


def _extract_text_from_pdf(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    texts = []

    for page in doc:
        native_text = page.get_text("text").strip()

        if len(native_text) > 20:
            texts.append(native_text)
        else:
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            img_bytes = pix.tobytes("png")
            image = Image.open(io.BytesIO(img_bytes))
            texts.append(pytesseract.image_to_string(image))

    return "\n".join(texts)


def _clean_number(value: str):
    try:
        return float(value.replace(",", "").strip())
    except:
        return None


def _extract_amount(text: str):
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    # PRIORITY 1: Grand Total (most important)
    for line in lines:
        if "grand" in line.lower() and "total" in line.lower():
            match = re.search(r"([0-9]+\.[0-9]{2})", line)
            if match:
                return _clean_number(match.group(1))

    # PRIORITY 2: Net / Final / Total
    for line in lines:
        line_lower = line.lower()

        if any(word in line_lower for word in ["bill no", "kot", "table", "covers", "waiter"]):
            continue

        if "total" in line_lower:
            match = re.search(r"([0-9]+\.[0-9]{2})", line)
            if match:
                return _clean_number(match.group(1))

    # PRIORITY 3: Subtotal fallback
    for line in lines:
        if "subtotal" in line.lower():
            match = re.search(r"([0-9]+\.[0-9]{2})", line)
            if match:
                return _clean_number(match.group(1))

    return None


def _extract_date(text: str):
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    for line in lines:
        if "date" in line.lower():
            # Fix OCR noise like 10-1.2-2025 → 10-12-2025
            cleaned = re.sub(r"[^\d/-]", "", line)

            match = re.search(r"(\d{1,2}[-/]\d{1,2}[-/]\d{4})", cleaned)
            if match:
                try:
                    dt = date_parser.parse(match.group(1), dayfirst=True)
                    return dt.date().isoformat()
                except:
                    pass

    return None


def _extract_merchant(text: str):
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    for line in lines[:6]:
        line_lower = line.lower()

        if any(word in line_lower for word in [
            "bill no", "date", "table", "covers", "waiter",
            "subtotal", "grand total", "kot", "qty", "rate", "amount"
        ]):
            continue

        if len(line) > 3 and not re.search(r"\d{3,}", line):
            return line[:80]

    return None


def extract_receipt_data(file_path: str):
    lower = file_path.lower()

    if lower.endswith(".pdf"):
        text = _extract_text_from_pdf(file_path)
    else:
        text = _extract_text_from_image(file_path)

    return {
        "merchant": _extract_merchant(text),
        "receipt_date": _extract_date(text),
        "detected_amount": _extract_amount(text),
        "raw_text": text[:3000]
    }
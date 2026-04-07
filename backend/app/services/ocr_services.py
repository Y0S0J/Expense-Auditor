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
    except Exception:
        return None


def _extract_amount(text: str):
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    FINAL_KEYWORDS = [
        "grand total",
        "total",
        "amount due",
        "amt due",
        "amount payable",
        "balance due",
        "net total"
    ]

    IGNORE_KEYWORDS = [
        "subtotal",
        "sub total",
        "tax",
        "gst",
        "cgst",
        "sgst",
        "vat",
        "round",
        "discount"
    ]

    # 🔥 Step 1: Search from bottom (most reliable)
    for line in reversed(lines):
        line_lower = line.lower()

        if any(ignore in line_lower for ignore in IGNORE_KEYWORDS):
            continue

        if any(keyword in line_lower for keyword in FINAL_KEYWORDS):
            matches = re.findall(r"([0-9]+\.[0-9]{2})", line)
            if matches:
                vals = [_clean_number(m) for m in matches]
                vals = [v for v in vals if v is not None]
                if vals:
                    return max(vals)

    # 🔥 Step 2: fallback → take largest number
    decimals = []
    for line in lines:
        matches = re.findall(r"\b([0-9]+\.[0-9]{2})\b", line)
        for m in matches:
            val = _clean_number(m)
            if val is not None:
                decimals.append(val)

    if decimals:
        return max(decimals)

    return None


def _extract_date(text: str):
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    # First try lines that mention date
    for line in lines:
        if "date" in line.lower():
            # Fix OCR noise by keeping only digits and separators
            cleaned = re.sub(r"[^0-9/\-:\s]", "", line)

            # Try dd-mm-yyyy or dd/mm/yyyy
            match = re.search(r"(\d{1,2}[-/]\d{1,2}[-/]\d{4})", cleaned)
            if match:
                try:
                    dt = date_parser.parse(match.group(1), dayfirst=True)
                    return dt.date().isoformat()
                except Exception:
                    pass

    # Fallback: any date-like pattern in first few lines
    for line in lines[:12]:
        cleaned = re.sub(r"[^0-9/\-:\s]", "", line)
        match = re.search(r"(\d{1,2}[-/]\d{1,2}[-/]\d{4})", cleaned)
        if match:
            try:
                dt = date_parser.parse(match.group(1), dayfirst=True)
                return dt.date().isoformat()
            except Exception:
                pass

    return None


def _extract_merchant(text: str):
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    for line in lines[:8]:
        line_lower = line.lower()

        if any(word in line_lower for word in [
            "bill no", "date", "table", "covers", "waiter",
            "subtotal", "grand total", "kot", "qty", "rate",
            "amount", "sgst", "cgst", "round-off"
        ]):
            continue

        if len(line) >= 3 and not re.search(r"\d{3,}", line):
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
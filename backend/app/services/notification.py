import io
import fitz
import pytesseract
from PIL import Image

from app.config import TESSERACT_CMD

pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD


def extract_text_from_policy(pdf_path: str) -> str:
    """
    Extract text from policy PDF.
    First tries native PDF text extraction.
    If text is too little, falls back to OCR on rendered page image.
    """
    doc = fitz.open(pdf_path)
    all_text = []

    for page in doc:
        text = page.get_text("text").strip()

        if len(text) < 30:
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            img_bytes = pix.tobytes("png")
            image = Image.open(io.BytesIO(img_bytes))
            text = pytesseract.image_to_string(image)

        all_text.append(text)

    return "\n".join(all_text).strip()
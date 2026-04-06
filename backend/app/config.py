import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
POLICY_DIR = os.path.join(DATA_DIR, "policies")
RECEIPT_DIR = os.path.join(DATA_DIR, "sample_receipts")

os.makedirs(POLICY_DIR, exist_ok=True)
os.makedirs(RECEIPT_DIR, exist_ok=True)

TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

GENERATED_RULES_PATH = os.path.join(POLICY_DIR, "generated_rules.json")
EXTRACTED_POLICY_TEXT_PATH = os.path.join(POLICY_DIR, "extracted_policy_text.txt")
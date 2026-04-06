from fastapi import APIRouter, UploadFile, File
import shutil
import os
import json

from app.config import POLICY_DIR, EXTRACTED_POLICY_TEXT_PATH, GENERATED_RULES_PATH
from app.services.policy_pdf_reader import extract_text_from_policy
from app.services.policy_rule_generator import generate_rules_from_text

router = APIRouter()


@router.post("/upload-policy")
async def upload_policy(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        return {"error": "Only PDF policy files are supported."}

    pdf_path = os.path.join(POLICY_DIR, file.filename)

    with open(pdf_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    extracted_text = extract_text_from_policy(pdf_path)

    with open(EXTRACTED_POLICY_TEXT_PATH, "w", encoding="utf-8") as f:
        f.write(extracted_text)

    rules = generate_rules_from_text(extracted_text)

    with open(GENERATED_RULES_PATH, "w", encoding="utf-8") as f:
        json.dump(rules, f, indent=4)

    return {
        "message": "Policy uploaded and rules generated successfully.",
        "policy_file": file.filename,
        "rules": rules
    }
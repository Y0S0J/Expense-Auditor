from fastapi import APIRouter, UploadFile, File, Form
import shutil
import os

router = APIRouter()

UPLOAD_DIR = "backend/app/data/sample_receipts"

os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_receipt(
    file: UploadFile = File(...),
    description: str = Form(...)
):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "message": "File uploaded successfully",
        "filename": file.filename,
        "description": description
    }
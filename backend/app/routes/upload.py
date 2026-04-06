from fastapi import APIRouter, UploadFile, File, Form
import shutil
import os

from app.config import RECEIPT_DIR

router = APIRouter()


@router.post("/upload")
async def upload_receipt(
    file: UploadFile = File(...),
    description: str = Form(...)
):
    file_path = os.path.join(RECEIPT_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "message": "Receipt uploaded successfully",
        "filename": file.filename,
        "description": description
    }
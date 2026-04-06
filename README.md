# Expense-Auditor
An AI-powered expense auditing system that uses OCR and policy parsing to automatically validate employee expense claims.

The system extracts structured data from receipts, converts company policy PDFs into rule-based constraints, and evaluates each expense for compliance. It flags inconsistencies, detects violations, and provides explainable approval, rejection, or review decisions.

# Problem
Manual expense auditing is slow, inconsistent and error-prone. Finance teams must review each receipt against complex policies, leading to delays and incorrect reimbursements.

# Solution
This project automates the auditing process by:
 
 -Extracting key details from receipts
 
 -Understanding company policy rules
 
 -Evaluating each expense against those rules
 
 -Returning a clear decision with reasoning

# How It Works
1. **Policy Ingestion**
   - Upload company policy as a PDF
   - Extract text using PDF parsing + OCR fallback
   - Convert policy into structured rules (JSON)

2. **Receipt Processing**
   - Upload receipt image or PDF
   - Extract text using OCR (Tesseract)
   - Identify merchant, date, and total amount

3. **Smart Field Extraction**
   - Detect amount using contextual keywords like:
     - Grand Total, Total, Amount Payable
   - Ignore irrelevant numbers (bill no, KOT, etc.)
   - Extract date from noisy OCR text

4. **Decision Engine**
   - Compare extracted values with claimed data
   - Apply policy rules (limits, restrictions)
   - Return:
     - ✅ Approved
     - ❌ Rejected
     - ⚠️ Flagged

 # How To Run
 1.**Go to the backend folder**: 
          
    cd backend

 2.**Install dependencies**:
          
    python -m pip install fastapi uvicorn python-multipart pymupdf pillow pytesseract python-dateutil

 
 3.**Install Tesseract OCR (Required)**:
   
   - Download from: https://github.com/UB-Mannheim/tesseract/wiki
   
   - Install and ensure path is set in `config.py`

 4.**Run server**:

    python -m uvicorn app.main:app --reload

 
 5.**Open frontend**:

   - Open `frontend/index.html` in your browser   

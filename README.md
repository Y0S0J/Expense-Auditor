# Expense-Auditor
An AI-powered expense auditing and approval system that uses OCR and policy-based validation to automatically review employee expense claims.

The system supports a full workflow involving employees, bosses and auditors. Employees first request claim approval with an estimated budget, bosses approve or decline the request, employees then submit the final receipt after the event and the system audits the claim against approved budgets, receipt details and company policy rules. Flagged claims are escalated to auditors for final review.

# Problem
Manual expense auditing is slow, inconsistent and error-prone. Finance and management teams must review each receipt against company policies, approved budgets and supporting documents, leading to delays, incorrect reimbursements and lack of accountability.

# Solution
This project automates the auditing process by:
 
 - Allowing employees to request claim approval before the expense occurs
 
 - Letting bosses approve or decline the estimated budget
 
 - Extracting key details from receipts using OCR
 
 - Applying company policy rules and approved budget checks
 
 - Deducting prohibited items where applicable
 
 - Returning a clear decision with reasoning
 
 - Escalating flagged claims to auditors for manual review

# How It Works
1. **Employee Request**
   - Employee submits a claim request before the event
   - Includes claim type, purpose, planned date and estimated budget
   - The request is stored with a unique internal sequence code

2. **Boss Approval**
   - The boss reviews pending claim requests
   - The boss can approve or decline the request
   - If approved, the boss sets the final approved budget
   - The employee is then allowed to submit the actual expense after the event

3. **Receipt Processing**
   - Employee uploads receipt image or PDF after the event
   - OCR (Tesseract) extracts receipt text
   - The system identifies merchant, date and final amount

4. **Smart Field Extraction**
   - Detect amount using contextual keywords like:
     - Grand Total, Total, Amount Payable, Amt Due, Balance Due
   - Ignore irrelevant numbers such as subtotal, tax-only values, bill numbers and KOT numbers
   - Extract date from noisy OCR text

5. **Decision Engine**
   - Compare extracted values with claimed data
   - Ensure the adjusted claim amount does not exceed the approved budget
   - Apply company policy rules such as limits and prohibited items
   - If prohibited items are found, deduct their value from the receipt total
   - Return:
     - ✅ Approved
     - ⚠️ Flagged
     - ❌ Declined
     - 🔁 Resubmit (through auditor review)

6. **Auditor Review**
   - Flagged claims are shown to the auditor
   - The auditor can inspect the uploaded receipt and system reasoning
   - The auditor can:
     - Approve the claim
     - Decline the claim
     - Ask the employee to resubmit corrected details

 # How To Run
 1.**Go to the backend folder**: 
          
    cd backend

 2.**Install dependencies**:
          
    python -m pip install fastapi uvicorn python-multipart pymupdf pillow pytesseract python-dateutil opencv-python rapidfuzz

 
 3.**Install Tesseract OCR (Required)**:
   
   - Download from: https://github.com/UB-Mannheim/tesseract/wiki
   
   - Install and ensure path is set in `config.py`

 4.**Run server**:

    python -m uvicorn app.main:app --reload

 
 5.**Open frontend**:

   - Open `http://127.0.0.1:8000` in your browser

 6.**Demo Login Credentials**:

   - Employee: `E001` / `emp123`
   - Boss: `B001` / `boss123`
   - Auditor: `A001` / `audit123`

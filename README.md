# Expense-Auditor
An AI-powered system that audits employee expense claims by comparing receipts against company policies. It automatically detects violations, flags inconsistencies and provides clear approval or rejection decisions, reducing manual effort and improving accuracy.

# Problem
Manual expense auditing is slow, inconsistent and error-prone. Finance teams must review each receipt against complex policies, leading to delays and incorrect reimbursements.

# Solution
This project automates the auditing process by:
 
 -Extracting key details from receipts
 -Understanding company policy rules
 -Evaluating each expense against those rules
 -Returning a clear decision with reasoning


 # How To Run
 1.Go to the backend folder
       cd backend

 2.Install dependencies
       python -m pip install fastapi uvicorn python-multipart

 3.Run the Server
       python -m uvicorn app.main:app --reload

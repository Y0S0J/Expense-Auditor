from fastapi import FastAPI
from app.routes import upload, audit

app = FastAPI(title="AI Expense Auditor")

# routes
app.include_router(upload.router)
app.include_router(audit.router)

@app.get("/")
def root():
    return {"message": "Expense Auditor API is running"}
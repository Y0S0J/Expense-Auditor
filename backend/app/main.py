from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import upload, audit, policy

app = FastAPI(title="AI Expense Auditor")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, tags=["Receipts"])
app.include_router(audit.router, tags=["Audit"])
app.include_router(policy.router, tags=["Policy"])


@app.get("/")
def root():
    return {"message": "Expense Auditor API is running 🚀"}
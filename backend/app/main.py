from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routes import auth, claims, submit, auditor
from app.database import init_db, seed_data

app = FastAPI()

init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(claims.router)
app.include_router(submit.router)
app.include_router(auditor.router)

init_db()
seed_data()

@app.get("/")
def root():
    return {"message": "Expense Auditor API running"}
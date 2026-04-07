from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pathlib import Path

from app.database import init_db, seed_data
from app.routes import auth, claims, boss, auditor, profile

app = FastAPI(title="AI Expense Auditor")

init_db()
seed_data()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(claims.router)
app.include_router(boss.router)
app.include_router(auditor.router)
app.include_router(profile.router)

# backend/app/main.py -> backend/app
APP_DIR = Path(__file__).resolve().parent
# backend
BACKEND_DIR = APP_DIR.parent
# project root
PROJECT_ROOT = BACKEND_DIR.parent

FRONTEND_DIR = PROJECT_ROOT / "frontend"
RECEIPTS_DIR = APP_DIR / "data" / "receipts"

# Make sure receipts folder exists
RECEIPTS_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")
app.mount("/receipts", StaticFiles(directory=str(RECEIPTS_DIR)), name="receipts")


@app.get("/")
def root():
    return RedirectResponse(url="/static/login.html")
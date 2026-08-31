import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import customers, sage_sync

load_dotenv()

app = FastAPI(title="JEM Leasing ERP API", version="0.1.0")

origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(customers.router)
app.include_router(sage_sync.router)


@app.get("/api/health")
def health_check():
    """Quick check that the API is up and can reach MySQL."""
    from app.database import db_cursor
    try:
        with db_cursor() as cur:
            cur.execute("SELECT 1")
            cur.fetchone()
        db_ok = True
    except Exception as e:
        db_ok = False
    return {"api": "ok", "database": "ok" if db_ok else "unreachable"}

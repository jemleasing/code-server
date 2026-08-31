import os
from dotenv import load_dotenv
load_dotenv()  # Load environment variables first

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 1. Initialize the app FIRST
app = FastAPI(title="JEM Leasing ERP API", version="0.1.0")

# 2. Add CORS middleware to the app instance
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Import and include your routers after app is initialized
from app.routers import customers, sage_sync

app.include_router(customers.router)
app.include_router(sage_sync.router)

origins = os.getenv("CORS_ORIGINS", "http://localhost:5173","https://code-server-tau.vercel.app/").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(customers.router)
# app.include_router(router)
# app.include_router(sage_sync.router)

@app.get("/")
def read_root():
    return {"status": "online", "message": "Livery ERP API is running"}

@app.get("/api/health/")
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

from app.database import db_cursor

@app.get("/api/leases/ar-summary/")
def get_lease_ar_summary():
    with db_cursor() as cursor:
        # Let's test grabbing just one row with a wildcard
        cursor.execute("SELECT * FROM tbllease LIMIT 1")
        row = cursor.fetchone()
        print("DEBUG LEASE ROW:", row)  # This will print to your backend terminal!
        
        cursor.execute("SELECT `Lease#` as LeaseNumber, LeaseID, CustomerID, Customer, AmountDue, LastPayDate FROM tbllease WHERE LeaseID BETWEEN 'A' and 'V' ORDER BY AmountDue DESC LIMIT 10")
        rows = cursor.fetchall()
        
    result = [
        {
            "LeaseNumber": row.get("LeaseNumber"),
            "Customer ID": row.get("CustomerID"),
            "Customer": row.get("Customer"),
            "Balance": row.get("AmountDue"),
            "Last Pay Date": str(row.get("LastPayDate")) if row.get("LastPayDate") else None,
            "Last Pay Amt": None,
            "SyncRunAt": "Live"
        } 
        for row in rows
    ]
    return {"customers": result}
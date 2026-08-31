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
from app.routers import customers, sage_sync, leases

app.include_router(customers.router)
app.include_router(sage_sync.router)

origins = os.getenv("CORS_ORIGINS", "https://localhost:5173,https://code-server-tau.vercel.app/").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(customers.router)
app.include_router(leases.router, prefix="/api")
app.include_router(sage_sync.router)

@app.get("/")
def read_root():
    return {"status": "online", "message": "Livery ERP API is running"}

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

from app.database import db_cursor


def _fetch_account_summary(limit: int | None = None):
    """
    Shared query behind both the AR summary panel (top 10 by balance) and
    the full account report: one row per customer, with all of that
    customer's leases (LeaseID starting with a letter A-V) collated
    together - lease numbers combined, balances and collateral values
    summed.
    """
    query = """
        SELECT
            l.CustomerID,
            l.Customer,
            GROUP_CONCAT(DISTINCT l.`Lease#` ORDER BY l.`Lease#` SEPARATOR ', ') AS LeaseNumbers,
            SUM(l.AmountDue) AS Balance,
            MAX(l.LastPayDate) AS LastPayDate,
            SUM(cv.CollatV) AS TotalCollatV
        FROM tbllease l
        LEFT JOIN (
            -- Pre-aggregate per lease first, so a lease with more than
            -- one tblcollatv row can't fan out the join and inflate
            -- the AmountDue sum above.
            SELECT LeaseID, SUM(CollatV) AS CollatV
            FROM tblcollatv
            GROUP BY LeaseID
        ) cv ON cv.LeaseID = l.LeaseID
        WHERE UPPER(SUBSTRING(l.LeaseID, 1, 1)) BETWEEN 'A' AND 'V'
        GROUP BY l.CustomerID, l.Customer
        ORDER BY Balance DESC
    """
    params = ()
    if limit is not None:
        query += " LIMIT %s"
        params = (limit,)

    with db_cursor() as cursor:
        cursor.execute(query, params)
        rows = cursor.fetchall()

    return [
        {
            "LeaseNumber": row.get("LeaseNumbers"),
            "Customer ID": row.get("CustomerID"),
            "Customer": row.get("Customer"),
            "Balance": row.get("Balance"),
            "Last Pay Date": str(row.get("LastPayDate")) if row.get("LastPayDate") else None,
            "Last Pay Amt": None,
            "CollatV": row.get("TotalCollatV"),
            "SyncRunAt": "Live"
        }
        for row in rows
    ]


@app.get("/api/leases/ar-summary")
def get_lease_ar_summary():
    """Top 10 highest AR balances, for the dashboard panel."""
    return {"customers": _fetch_account_summary(limit=10)}


@app.get("/api/leases/account-report")
def get_account_report():
    """
    Full report: every customer with a lease account starting with a
    letter A through V (no limit), for the account report page.
    """
    return {"customers": _fetch_account_summary(limit=None)}
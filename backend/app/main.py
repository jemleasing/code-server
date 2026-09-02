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
    together - lease numbers, vehicle make/model, balances and
    collateral values all combined.
    """
    query = """
        SELECT
            l.CustomerID,
            l.Customer,
            GROUP_CONCAT(DISTINCT l.`Lease#` ORDER BY l.`Lease#` SEPARATOR ', ') AS LeaseNumbers,
            GROUP_CONCAT(DISTINCT CONCAT(car.Make, ' ', car.Model) ORDER BY car.Make SEPARATOR ', ') AS Vehicles,
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
        LEFT JOIN tbl_b_car car ON car.Vin = l.VIN
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
            "Vehicle": row.get("Vehicles"),
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


@app.get("/api/leases/active-collatv")
def get_active_collatv():
    """
    One row per active account (Active = 1): account/lease number,
    customer, balance, and CollatV. Unlike the account report above,
    this is NOT collated per customer - each active lease gets its own
    row, so a customer with two active leases shows up twice.
    """
    with db_cursor() as cursor:
        cursor.execute(
            """
            SELECT
                l.LeaseID,
                l.`Lease#` AS LeaseNumber,
                l.CustomerID,
                l.Customer,
                l.AmountDue AS Balance,
                cv.CollatV
            FROM tbllease l
            LEFT JOIN (
                SELECT LeaseID, SUM(CollatV) AS CollatV
                FROM tblcollatv
                GROUP BY LeaseID
            ) cv ON cv.LeaseID = l.LeaseID
            WHERE l.Active = 1
            ORDER BY l.`Lease#`
            """
        )
        rows = cursor.fetchall()

    return {
        "accounts": [
            {
                "LeaseID": row.get("LeaseID"),
                "LeaseNumber": row.get("LeaseNumber"),
                "Customer ID": row.get("CustomerID"),
                "Customer": row.get("Customer"),
                "Balance": row.get("Balance"),
                "CollatV": row.get("CollatV"),
            }
            for row in rows
        ]
    }


@app.get("/api/leases/active-full-report")
def get_active_full_report():
    """
    One row per active account (Active = 1): balance, CollatV pulled from
    every source table that has one, and vehicle year/make/model/cost/
    current value.

    tblscorecard and tbl_productsearcheditquery are both history/import
    logs with no unique key on Lease#/LeaseID (multiple rows can exist
    per lease over time), so each is narrowed down to its latest row per
    lease via a MAX(ID) subquery before joining - otherwise the join
    would fan out and duplicate/inflate every other column in the row.
    Same idea for tblcarcurrentvalue, keyed by latest DateInspected/ID
    per VIN.
    """
    with db_cursor() as cursor:
        cursor.execute(
            """
            SELECT
                l.LeaseID,
                l.`Lease#` AS LeaseNumber,
                l.CustomerID,
                l.Customer,
                l.AmountDue AS Balance,

                cv.CollatV AS CollatV_TblCollatv,
                sc.CollatV AS CollatV_Scorecard,
                psq.collatV1 AS CollatV_ProductSearch,

                car.Year,
                car.Make,
                car.Model,
                car.PurchasePrice AS Cost,
                COALESCE(ccv.ADJEstMMR, ccv.MMR) AS CurrentValue

            FROM tbllease l

            LEFT JOIN (
                SELECT LeaseID, SUM(CollatV) AS CollatV
                FROM tblcollatv
                GROUP BY LeaseID
            ) cv ON cv.LeaseID = l.LeaseID

            LEFT JOIN (
                SELECT sc1.`Lease#`, sc1.CollatV
                FROM tblscorecard sc1
                INNER JOIN (
                    SELECT `Lease#`, MAX(ID) AS MaxID
                    FROM tblscorecard
                    GROUP BY `Lease#`
                ) latest ON latest.`Lease#` = sc1.`Lease#` AND latest.MaxID = sc1.ID
            ) sc ON sc.`Lease#` = l.`Lease#`

            LEFT JOIN (
                SELECT q1.LeaseID, q1.collatV1
                FROM tbl_productsearcheditquery q1
                INNER JOIN (
                    SELECT LeaseID, MAX(ID) AS MaxID
                    FROM tbl_productsearcheditquery
                    GROUP BY LeaseID
                ) latest ON latest.LeaseID = q1.LeaseID AND latest.MaxID = q1.ID
            ) psq ON psq.LeaseID = l.LeaseID

            LEFT JOIN tbl_b_car car ON car.Vin = l.VIN

            LEFT JOIN (
                SELECT ccv1.Vin, ccv1.MMR, ccv1.ADJEstMMR
                FROM tblcarcurrentvalue ccv1
                INNER JOIN (
                    SELECT Vin, MAX(ID) AS MaxID
                    FROM tblcarcurrentvalue
                    GROUP BY Vin
                ) latest ON latest.Vin = ccv1.Vin AND latest.MaxID = ccv1.ID
            ) ccv ON ccv.Vin = l.VIN

            WHERE l.Active = 1
            ORDER BY l.`Lease#`
            """
        )
        rows = cursor.fetchall()

    return {
        "accounts": [
            {
                "LeaseID": row.get("LeaseID"),
                "LeaseNumber": row.get("LeaseNumber"),
                "Customer ID": row.get("CustomerID"),
                "Customer": row.get("Customer"),
                "Balance": row.get("Balance"),
                "CollatV_TblCollatv": row.get("CollatV_TblCollatv"),
                "CollatV_Scorecard": row.get("CollatV_Scorecard"),
                "CollatV_ProductSearch": row.get("CollatV_ProductSearch"),
                "Year": row.get("Year"),
                "Make": row.get("Make"),
                "Model": row.get("Model"),
                "Cost": row.get("Cost"),
                "CurrentValue": row.get("CurrentValue"),
            }
            for row in rows
        ]
    }


@app.get("/api/leases/ezpass-violations")
def get_ezpass_violations():
    """
    Every customer with at least one EZPass toll violation in the last
    180 days: ticket count, account balance, CollatV, and current car
    value, collated one row per customer.

    NOTE on the EZPass filter: tbl_b_tickets holds all ticket types
    (parking, camera, tolls), not just EZPass. There's no live data
    available to confirm the exact Agency/Authority string used for
    EZPass records, so this filters on TollBill# being populated
    (a toll-specific field) OR Agency/Authority mentioning "EZ" as a
    reasonable default. Run the diagnostic query in
    sql/diagnose_ezpass_filter.sql against real data and adjust the
    WHERE clause below if it doesn't match what you expect.
    """
    with db_cursor() as cursor:
        cursor.execute(
            """
            SELECT
                l.CustomerID,
                l.Customer,
                GROUP_CONCAT(DISTINCT l.`Lease#` ORDER BY l.`Lease#` SEPARATOR ', ') AS LeaseNumbers,
                SUM(l.AmountDue) AS Balance,
                SUM(cv.CollatV) AS TotalCollatV,
                SUM(ccv.CurrentValue) AS TotalCurrentValue,
                SUM(tix.TicketCount) AS TicketCount
            FROM tbllease l
            INNER JOIN (
                SELECT `Lease#`, COUNT(*) AS TicketCount
                FROM tbl_b_tickets
                WHERE DateTimeOfViolation >= NOW() - INTERVAL 180 DAY
                  AND (
                      (`TollBill#` IS NOT NULL AND `TollBill#` != '')
                      OR Agency LIKE '%EZ%'
                      OR Authority LIKE '%EZ%PASS%'
                  )
                GROUP BY `Lease#`
            ) tix ON tix.`Lease#` = l.`Lease#`
            LEFT JOIN (
                SELECT LeaseID, SUM(CollatV) AS CollatV
                FROM tblcollatv
                GROUP BY LeaseID
            ) cv ON cv.LeaseID = l.LeaseID
            LEFT JOIN (
                SELECT ccv1.Vin, COALESCE(ccv1.ADJEstMMR, ccv1.MMR) AS CurrentValue
                FROM tblcarcurrentvalue ccv1
                INNER JOIN (
                    SELECT Vin, MAX(ID) AS MaxID
                    FROM tblcarcurrentvalue
                    GROUP BY Vin
                ) latest ON latest.Vin = ccv1.Vin AND latest.MaxID = ccv1.ID
            ) ccv ON ccv.Vin = l.VIN
            GROUP BY l.CustomerID, l.Customer
            ORDER BY TicketCount DESC
            """
        )
        rows = cursor.fetchall()

    return {
        "customers": [
            {
                "Customer ID": row.get("CustomerID"),
                "Customer": row.get("Customer"),
                "LeaseNumber": row.get("LeaseNumbers"),
                "TicketCount": row.get("TicketCount"),
                "Balance": row.get("Balance"),
                "CollatV": row.get("TotalCollatV"),
                "CurrentValue": row.get("TotalCurrentValue"),
            }
            for row in rows
        ]
    }
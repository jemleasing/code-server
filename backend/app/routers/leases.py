from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any
from app.database import get_connection # Assuming your DB dependency is here

router = APIRouter(prefix="/api/leases", tags=["leases"])

@router.get("/ar-summary/")
def get_ar_summary():
    # Return placeholder or query database for actual AR balances
    return []

@router.get("/active-full-report")
def get_active_full_report(db: Session = Depends(get_connection)):
    # 1. This proves the file is actually running
    print("=========================================")
    print("!!! ACTIVE FULL REPORT ENDPOINT HIT !!!")
    print("=========================================")
    
    # 2. No try/except block. If it fails, we WANT it to crash and show the error.
    query = text("SELECT * FROM tbllease LIMIT 5")
    result = db.execute(query).mappings().fetchall()
    
    data = [dict(row) for row in result]
    
    # 3. This proves if it actually found data
    print(f"!!! FOUND {len(data)} ROWS !!!")
    print("=========================================")
    
    return {"accounts": data}


@router.get("/active-collatv")
def get_active_collateral_value(db: Session = Depends(get_connection)) -> List[Dict[str, Any]]:
    # Changed JOIN to LEFT JOIN to prevent missing collateral data from hiding active leases
    query = text("""
        SELECT 
            l.`Lease#`, l.Customer, l.VIN,
            cv.CollatV, cv.CreditLimit, cv.InsuranceDP, cv.WeeksRemaining
        FROM tbllease l
        LEFT JOIN tblcollatv cv ON l.`Lease#` = cv.`Lease#`
        WHERE l.Active != 0
        ORDER BY cv.CollatV DESC
        LIMIT 100
    """)
    
    result = db.execute(query).mappings().fetchall()
    return [dict(row) for row in result]
    
    result = db.execute(query).mappings().fetchall()
    return [dict(row) for row in result]


@router.get("/account-report")
def get_account_report(lease_num: str = None, db: Session = Depends(get_connection)) -> Dict[str, Any]:
    """
    Returns a deep-dive on a specific account, including payment history and status flags.
    If no lease_num is provided, it can return a high-level summary of all accounts.
    """
    if not lease_num:
        # Barry's base endpoint hit. Return a high-level ledger summary.
        query = text("""
            SELECT 
                `Lease#` as lease_num, 
                COUNT(*) as total_payments, 
                SUM(Amount) as total_paid,
                MAX(DateTime) as last_payment_date
            FROM dbo_payments
            WHERE Void = 0
            GROUP BY `Lease#`
            ORDER BY last_payment_date DESC
            LIMIT 10
        """)
        result = db.execute(query).mappings().fetchall()
        return {"summary": [dict(row) for row in result]}

    # Specific account lookup
    lease_query = text("SELECT * FROM tbllease WHERE `Lease#` = :lease_num LIMIT 1")
    lease_data = db.execute(lease_query, {"lease_num": lease_num}).mappings().fetchone()
    
    if not lease_data:
        raise HTTPException(status_code=404, detail="Account not found")

    payments_query = text("""
        SELECT PaymentID, Amount, DateTime, PaymentType, BalanceAfterPayment 
        FROM dbo_payments 
        WHERE AccountID = :lease_num AND Void = 0
        ORDER BY DateTime DESC LIMIT 10
    """)
    payments_data = db.execute(payments_query, {"lease_num": lease_num}).mappings().fetchall()

    return {
        "account_details": dict(lease_data),
        "recent_payments": [dict(row) for row in payments_data]
    }
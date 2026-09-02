from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any
from app.database import get_db # Assuming your DB dependency is here

router = APIRouter(prefix="/api/leases", tags=["leases"])

@router.get("/ar-summary/")
def get_ar_summary():
    # Return placeholder or query database for actual AR balances
    return []

@router.get("/active-full-report")
def get_active_full_report(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
<<<<<<< HEAD
    """
    Returns a master list of all active leases, joining vehicle and customer data.
    Uses Active = -1 to account for legacy MS Access boolean formatting.
    """
=======
>>>>>>> 9676aef9ae093cdc8a7f12c65d7a0b227c129dfa
    query = text("""
        SELECT 
            l.ID, l.`Lease#`, l.Customer, l.Phone, l.AmountDue, l.LastPayDate, l.Coll_Status,
            c.Make, c.Model, c.Year, c.LicensePlate,
            cust.EstMilesPerWeek, cust.BaseName
        FROM tbllease l
        LEFT JOIN tbl_b_car c ON l.VIN = c.Vin
        LEFT JOIN tbl_b_customer cust ON l.`Lease#` = cust.`Lease#`
        WHERE l.Active = -1
        ORDER BY l.AmountDue DESC
<<<<<<< HEAD
=======
        LIMIT 100
>>>>>>> 9676aef9ae093cdc8a7f12c65d7a0b227c129dfa
    """)
    
    result = db.execute(query).mappings().fetchall()
    return [dict(row) for row in result]


@router.get("/active-collatv")
def get_active_collateral_value(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
<<<<<<< HEAD
    """
    Returns fleet exposure by linking active leases to their collateral values.
    """
=======
>>>>>>> 9676aef9ae093cdc8a7f12c65d7a0b227c129dfa
    query = text("""
        SELECT 
            l.`Lease#`, l.Customer, l.VIN,
            cv.CollatV, cv.CreditLimit, cv.InsuranceDP, cv.WeeksRemaining
        FROM tbllease l
        JOIN tblcollatv cv ON l.`Lease#` = cv.`Lease#`
        WHERE l.Active = -1
        ORDER BY cv.CollatV DESC
<<<<<<< HEAD
=======
        LIMIT 10
>>>>>>> 9676aef9ae093cdc8a7f12c65d7a0b227c129dfa
    """)
    
    result = db.execute(query).mappings().fetchall()
    return [dict(row) for row in result]


@router.get("/account-report")
def get_account_report(lease_num: str = None, db: Session = Depends(get_db)) -> Dict[str, Any]:
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
<<<<<<< HEAD
            LIMIT 100
=======
            LIMIT 10
>>>>>>> 9676aef9ae093cdc8a7f12c65d7a0b227c129dfa
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
<<<<<<< HEAD
        ORDER BY DateTime DESC LIMIT 50
=======
        ORDER BY DateTime DESC LIMIT 10
>>>>>>> 9676aef9ae093cdc8a7f12c65d7a0b227c129dfa
    """)
    payments_data = db.execute(payments_query, {"lease_num": lease_num}).mappings().fetchall()

    return {
        "account_details": dict(lease_data),
        "recent_payments": [dict(row) for row in payments_data]
    }
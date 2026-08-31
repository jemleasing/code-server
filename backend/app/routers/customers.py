from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.database import db_cursor

router = APIRouter(prefix="/api/customers", tags=["customers"])


@router.get("")
def search_leases(
    search: Optional[str] = Query(None, description="Search lease#, name, or VIN"),
    limit: int = Query(50, le=200),
    offset: int = 0,
):
    # Base filter restricting LeaseID to letters A through V
    base_where = "WHERE (UPPER(SUBSTRING(l.LeaseID, 1, 1)) BETWEEN 'A' AND 'V')"
    params = []
    
    if search:
        search_clean = search.strip()
        # Check if the search term looks like a car number (e.g., 5 digits or numbers before a dash)
        base_where += """ AND (
            l.`Lease#` LIKE %s 
            OR l.Customer LIKE %s 
            OR l.VIN LIKE %s 
            OR SUBSTRING_INDEX(l.`Lease#`, '-', 1) LIKE %s
        )"""
        like = f"%{search_clean}%"
        car_num_like = f"{search_clean}%"
        params = [like, like, like, car_num_like]

    query = f"""
        SELECT 
            l.LeaseID, 
            l.`Lease#` AS LeaseNumber, 
            l.CustomerID, 
            l.Customer, 
            l.VIN, 
            l.AmountDue, 
            l.LastPayDate,
            l.Active
        FROM tbllease l
        {base_where}
        ORDER BY l.LeaseID ASC
        LIMIT %s OFFSET %s
    """
    params += [limit, offset]

    with db_cursor() as cur:
        cur.execute(query, params)
        rows = cur.fetchall()
        
    return {"customers": rows, "limit": limit, "offset": offset}


@router.get("/{customer_id}")
def get_customer(customer_id: int):
    with db_cursor() as cur:
        cur.execute("SELECT * FROM tbl_b_customer WHERE CustomerID = %s", (customer_id,))
        row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Customer not found")
    return row


@router.get("/{customer_id}/payments")
def get_customer_payments(customer_id: int, limit: int = Query(50, le=200)):
    with db_cursor() as cur:
        cur.execute(
            """
            SELECT c.`Lease#` AS LeaseNumber
            FROM tbl_b_customer c WHERE c.CustomerID = %s
            """,
            (customer_id,),
        )
        cust = cur.fetchone()
        if not cust:
            raise HTTPException(status_code=404, detail="Customer not found")

        cur.execute(
            """
            SELECT p.PaymentID, p.PaymentType, p.Amount, p.DateTime,
                   p.CheckNo, p.SageExportedAt, pt.`Account#` AS GLAccount
            FROM dbo_payments p
            LEFT JOIN dbo_paymenttypes pt ON pt.Name = p.PaymentType
            WHERE p.AccountID = %s
            ORDER BY p.DateTime DESC
            LIMIT %s
            """,
            (cust["LeaseNumber"], limit),
        )
        rows = cur.fetchall()
    return {"customer_id": customer_id, "payments": rows}
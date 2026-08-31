from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.database import db_cursor

router = APIRouter(prefix="/api/customers", tags=["customers"])


@router.get("")
def list_customers(
    search: Optional[str] = Query(None, description="Search name, lease#, or VIN"),
    limit: int = Query(50, le=200),
    offset: int = 0,
):
    """
    Customer list, matching the fields already used across the Access app
    (tbl_b_customer). Supports a simple search across name/lease/VIN so this
    can back a lookup screen similar to what Access currently offers.
    """
    where = ""
    params = []
    if search:
        where = """
            WHERE CustFirstName LIKE %s OR CustLastName LIKE %s
               OR `Lease#` LIKE %s OR VIN LIKE %s
        """
        like = f"%{search}%"
        params = [like, like, like, like]

    query = f"""
        SELECT CustomerID, `Lease#` AS LeaseNumber, CustFirstName, CustLastName,
               CustCurrentAddress1, CustCurrentCity, CustCurrentState, CustCurrentZip,
               VIN, CustStatus, CollStatus
        FROM tbl_b_customer
        {where}
        ORDER BY CustLastName, CustFirstName
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
    """
    Payment history for one customer, joined to payment type so the GL
    mapping used in the Sage export is visible here too.
    """
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

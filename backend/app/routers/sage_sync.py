from fastapi import APIRouter, Query

from app.database import db_cursor

router = APIRouter(prefix="/api/sage-sync", tags=["sage-sync"])


@router.get("/status")
def sync_status(limit: int = Query(20, le=100)):
    """
    Recent sync run history from tblSageSyncLog - lets staff see, from a
    browser, whether last night's Sage<->MySQL sync ran and whether
    anything failed, without opening a MySQL client or checking logs on
    the server directly.
    """
    with db_cursor() as cur:
        cur.execute(
            """
            SELECT ID, Direction, StartedAt, FinishedAt, RowsProcessed,
                   RowsFailed, Status, Detail
            FROM tblSageSyncLog
            ORDER BY StartedAt DESC
            LIMIT %s
            """,
            (limit,),
        )
        runs = cur.fetchall()
    return {"runs": runs}


@router.get("/pending-exports")
def pending_exports(limit: int = Query(100, le=500)):
    """
    Cash receipts not yet sent to Sage - the daily queue that
    mysql_to_sage_export.py works through. Visible here so staff can spot-
    check what's about to go out (or why something hasn't gone out yet)
    before it's automated end-to-end.
    """
    with db_cursor() as cur:
        cur.execute(
            """
            SELECT p.PaymentID, p.AccountID, p.CustName, p.PaymentType,
                   p.Amount, p.DateTime, p.CheckNo, p.SageExportError
            FROM dbo_payments p
            WHERE (p.Void IS NULL OR p.Void = 0)
              AND p.SageExportedAt IS NULL
            ORDER BY p.DateTime ASC
            LIMIT %s
            """,
            (limit,),
        )
        rows = cur.fetchall()
    return {"pending": rows, "count": len(rows)}


@router.get("/ar-summary")
def ar_summary(limit: int = Query(50, le=200)):
    """
    Latest customer AR balances pulled from Sage overnight, straight from
    tblSageARImport - this is the browser-facing replacement for opening
    the Excel file that used to get manually imported each morning.
    """
    with db_cursor() as cur:
        cur.execute(
            """
            SELECT `Customer ID`, `Customer`, `Balance`, `Last Pay Date`,
                   `Last Pay Amt`, SyncRunAt
            FROM tblSageARImport
            ORDER BY `Balance` DESC
            LIMIT %s
            """,
            (limit,),
        )
        rows = cur.fetchall()
    return {"customers": rows}

from fastapi import APIRouter

router = APIRouter(prefix="/api/leases", tags=["leases"])

@router.get("/ar-summary/")
def get_ar_summary():
    # Return placeholder or query database for actual AR balances
    return []
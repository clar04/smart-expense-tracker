from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from datetime import date
from typing import Optional, Any, Dict
from app.models.transaction import Transaction

router = APIRouter(prefix="/transactions", tags=["transactions"])

class TxIn(BaseModel):
    date: date
    description: str
    amount: float
    merchant: Optional[str] = None
    category_id: Optional[str] = None
    predicted_category: Optional[str] = None
    predicted_proba: Optional[float] = None
    source: Optional[str] = "manual"

@router.post("")
async def create_transaction(payload: TxIn):
    doc = Transaction(**payload.model_dump())
    saved = await doc.insert()
    return {"id": str(saved.id)}

# -------- LIST (GET) --------
@router.get("")
async def list_transactions(
    start: Optional[date] = Query(None, description="YYYY-MM-DD"),
    end: Optional[date] = Query(None, description="YYYY-MM-DD"),
    category_id: Optional[str] = None,
    q: Optional[str] = Query(None, description="search in description/merchant (case-insensitive)"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=200),
    sort: str = Query("-created_at", description="prefix '-' = desc, contoh: -created_at atau date"),
):
    criteria: Dict[str, Any] = {}

    if category_id:
        criteria["category_id"] = category_id

    if start or end:
        d: Dict[str, Any] = {}
        if start: d["$gte"] = start
        if end:   d["$lte"] = end
        criteria["date"] = d

    if q:
        criteria["$or"] = [
            {"description": {"$regex": q, "$options": "i"}},
            {"merchant": {"$regex": q, "$options": "i"}},
        ]

    skip = (page - 1) * limit
    cursor = Transaction.find(criteria).sort(sort)
    total = await Transaction.find(criteria).count()
    items = await cursor.skip(skip).limit(limit).to_list()

    return {
        "items": items,
        "page": page,
        "limit": limit,
        "total": total,
        "has_next": (skip + len(items)) < total,
    }

# -------- DELETE (opsional) --------
@router.delete("/{tx_id}")
async def delete_transaction(tx_id: str):
    doc = await Transaction.get(tx_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Transaction not found")
    await doc.delete()
    return {"deleted": True}

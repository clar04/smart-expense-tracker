from beanie import Document
from pydantic import Field, BaseModel
from datetime import datetime, date
from typing import Optional, List, Any, Dict
from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/transactions", tags=["transactions"])

class Transaction(Document):
    user_id: Optional[str] = None
    date: date
    description: str = ""
    amount: float = 0.0
    merchant: Optional[str] = None
    category_id: Optional[str] = None
    predicted_category: Optional[str] = None
    predicted_proba: Optional[float] = None
    source: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "transactions"

# --- Schemas ---
class TxIn(BaseModel):
    date: date
    description: str
    amount: float
    merchant: Optional[str] = None
    category_id: Optional[str] = None
    predicted_category: Optional[str] = None
    predicted_proba: Optional[float] = None
    source: Optional[str] = "manual"

class TxOut(BaseModel):
    id: str

# --- Create ---
@router.post("", response_model=TxOut)
async def create_transaction(payload: TxIn):
    doc = Transaction(**payload.model_dump())
    saved = await doc.insert()
    return {"id": str(saved.id)}

# --- List with filters/pagination ---
@router.get("")
async def list_transactions(
    start: Optional[date] = Query(None, description="YYYY-MM-DD"),
    end: Optional[date] = Query(None, description="YYYY-MM-DD"),
    category_id: Optional[str] = None,
    q: Optional[str] = Query(None, description="search in description/merchant (case-insensitive)"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=200),
    sort: str = Query("-created_at", description="field to sort, prefix '-' = desc"),
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
    cursor = Transaction.find(criteria)

    # sorting: e.g. "-created_at" or "date"
    cursor = cursor.sort(sort)

    total = await Transaction.find(criteria).count()
    items = await cursor.skip(skip).limit(limit).to_list()

    # Beanie returns Documents; FastAPI will JSONify them nicely
    return {
        "items": items,
        "page": page,
        "limit": limit,
        "total": total,
        "has_next": (skip + len(items)) < total,
    }

# --- Delete ---
@router.delete("/{tx_id}")
async def delete_transaction(tx_id: str):
    doc = await Transaction.get(tx_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Transaction not found")
    await doc.delete()
    return {"deleted": True}
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, Any, Dict
from app.models.transaction import Transaction

router = APIRouter(prefix="/transactions", tags=["transactions"])

class TxIn(BaseModel):
    date: date
    description: str = Field(min_length=1)
    amount: float = Field(gt=0)
    merchant: Optional[str] = None
    category_id: Optional[str] = None
    predicted_category: Optional[str] = None
    predicted_proba: Optional[float] = None
    source: Optional[str] = "manual"

class TxBulkIn(BaseModel):
    items: list[TxIn]

class TxUpdate(BaseModel):
    date: Optional[date] = None
    description: Optional[str] = None
    amount: Optional[float] = None
    merchant: Optional[str] = None
    category_id: Optional[str] = None
    predicted_category: Optional[str] = None
    predicted_proba: Optional[float] = None
    source: Optional[str] = None

@router.post("")
async def create_transaction(payload: TxIn):
    doc = Transaction(**payload.model_dump())
    saved = await doc.insert()
    return {"id": str(saved.id)}

@router.get("/{tx_id}")
async def get_transaction(tx_id: str):
    doc = await Transaction.get(tx_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return doc

@router.patch("/{tx_id}")
async def update_transaction(tx_id: str, payload: TxUpdate):
    doc = await Transaction.get(tx_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Transaction not found")

    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(doc, k, v)
    await doc.save()
    return {"updated": True}

@router.get("")
async def list_transactions(
    start: Optional[date] = Query(None),
    end: Optional[date] = Query(None),
    category_id: Optional[str] = None,
    q: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=200),
    sort: str = Query("-created_at"),
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

@router.delete("/{tx_id}")
async def delete_transaction(tx_id: str):
    doc = await Transaction.get(tx_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Transaction not found")
    await doc.delete()
    return {"deleted": True}

@router.post("/bulk")
async def create_transactions_bulk(payload: TxBulkIn):
    docs = [Transaction(**it.model_dump()) for it in payload.items]
    res = await Transaction.insert_many(docs)
    return {"inserted": len(res.inserted_ids), "ids": [str(i) for i in res.inserted_ids]}
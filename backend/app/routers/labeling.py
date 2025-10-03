from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from app.models.transaction import Transaction

router = APIRouter(prefix="/labeling", tags=["labeling"])

class LabelIn(BaseModel):
    category_id: Optional[str] = None  

@router.get("/unlabeled")
async def get_unlabeled(
    limit: int = Query(50, ge=1, le=200),
    q: Optional[str] = Query(None, description="cari di description/merchant (case-insensitive)")
):
    crit: Dict[str, Any] = {"category_id": None}
    if q:
        crit["$or"] = [
            {"description": {"$regex": q, "$options": "i"}},
            {"merchant": {"$regex": q, "$options": "i"}},
        ]
    txs: List[Transaction] = await Transaction.find(crit).sort("-created_at").limit(limit).to_list()
    items = [
        {
            "id": str(t.id),
            "date": t.date,
            "description": t.description,
            "merchant": t.merchant,
            "amount": t.amount,
            "category_id": t.category_id,
        }
        for t in txs
    ]
    return {"items": items}

@router.post("/{tx_id}")
async def set_label(tx_id: str, body: LabelIn):
    doc = await Transaction.get(tx_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Transaction not found")
    doc.category_id = body.category_id
    await doc.save()
    return {"updated": True, "category_id": doc.category_id}

@router.get("/stats")
async def labeling_stats():
    cnt_unlabeled = await Transaction.find(Transaction.category_id == None).count() 
    cnt_total = await Transaction.find_all().count()
    return {"unlabeled": cnt_unlabeled, "total": cnt_total}
from fastapi import APIRouter, Query
from typing import Optional, List, Dict, Any
from datetime import date, time, datetime
from app.models.transaction import Transaction
from app.models.category import Category

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/summary")
async def summary(
    start: Optional[date] = Query(None),
    end: Optional[date] = Query(None),
):
    coll = Transaction.get_pymongo_collection()
    match: Dict[str, Any] = {}
    if start or end:
        d: Dict[str, Any] = {}
        if start: 
            start_dt = datetime.combine(start, time.min)
            d["$gte"] = start_dt
        if end:   
            end_dt = datetime.combine(end, time.max)
            d["$lte"] = end_dt
        match["date"] = d

    pipeline = []
    if match:
        pipeline.append({"$match": match})
    pipeline += [
        {"$group": {
            "_id": "$category_id",
            "totalAmount": {"$sum": "$amount"},
            "count": {"$sum": 1}
        }},
        {"$sort": {"totalAmount": -1}}
    ]

    rows = await coll.aggregate(pipeline).to_list(length=1000)

    # map id -> name
    cats = await Category.find_all().to_list()
    names = {str(c.id): c.name for c in cats}

    def resolve_name(cid):
        if cid is None:
            return "Uncategorized"
        return names.get(cid, f"(deleted:{cid})")

    items = [
        {"category_id": r["_id"], "category_name": resolve_name(r["_id"]),
         "total": r["totalAmount"], "count": r["count"]}
        for r in rows
    ]
    totals = {
        "grand_total": sum(i["total"] for i in items),
        "tx_count": sum(i["count"] for i in items),
    }
    return {"items": items, "totals": totals}

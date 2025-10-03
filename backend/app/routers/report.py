# app/routers/reports.py
from fastapi import APIRouter, Query
from typing import Optional, Dict, Any, List
from datetime import date
from collections import defaultdict
from app.models.transaction import Transaction
from app.models.category import Category

router = APIRouter(prefix="/reports", tags=["reports"])

def _get_collection():
    """
    Beberapa versi Beanie expose:
      - get_motor_collection()  (baru, Motor Async)
      - get_collection()        (lama)
    Pakai yang tersedia.
    """
    m = getattr(Transaction, "get_motor_collection", None)
    if callable(m):
        return Transaction.get_motor_collection()
    g = getattr(Transaction, "get_collection", None)
    if callable(g):
        return Transaction.get_collection()
    raise RuntimeError("Tidak menemukan accessor koleksi Mongo untuk Transaction")

@router.get("/summary")
async def summary(
    start: Optional[date] = Query(None),
    end: Optional[date] = Query(None),
):
    # Bangun filter match (pakai type 'date' saja)
    match: Dict[str, Any] = {}
    if start or end:
        d: Dict[str, Any] = {}
        if start: d["$gte"] = start
        if end:   d["$lte"] = end
        match["date"] = d

    # Coba aggregation di Mongo dulu
    try:
        coll = _get_collection()
        pipeline: List[Dict[str, Any]] = []
        if match:
            pipeline.append({"$match": match})
        pipeline += [
            {"$group": {
                "_id": "$category_id",
                "totalAmount": {"$sum": "$amount"},
                "count": {"$sum": 1},
            }},
            {"$sort": {"totalAmount": -1}},
        ]
        rows = await coll.aggregate(pipeline).to_list(length=2000)

        # map id -> name
        cats = await Category.find_all().to_list()
        names = {str(c.id): c.name for c in cats}

        def resolve_name(cid):
            if cid is None:
                return "Uncategorized"
            return names.get(cid, f"(deleted:{cid})")

        items = [
            {
                "category_id": r["_id"],
                "category_name": resolve_name(r["_id"]),
                "total": float(r.get("totalAmount", 0.0)),
                "count": int(r.get("count", 0)),
            }
            for r in rows
        ]
        totals = {
            "grand_total": sum(i["total"] for i in items),
            "tx_count": sum(i["count"] for i in items),
        }
        return {"items": items, "totals": totals}

    except Exception:
        # Fallback aman di Python (lebih lambat tapi anti-500)
        qry = Transaction.find(match) if match else Transaction.find_all()
        txs = await qry.to_list()
        cats = await Category.find_all().to_list()
        names = {str(c.id): c.name for c in cats}

        bucket_total = defaultdict(float)
        bucket_count = defaultdict(int)
        for t in txs:
            cid = t.category_id
            bucket_total[cid] += float(t.amount or 0.0)
            bucket_count[cid] += 1

        def resolve_name(cid):
            if cid is None:
                return "Uncategorized"
            return names.get(cid, f"(deleted:{cid})")

        items = [
            {
                "category_id": cid,
                "category_name": resolve_name(cid),
                "total": total,
                "count": bucket_count[cid],
            }
            for cid, total in sorted(bucket_total.items(), key=lambda kv: kv[1], reverse=True)
        ]
        totals = {
            "grand_total": sum(bucket_total.values()),
            "tx_count": sum(bucket_count.values()),
        }
        return {"items": items, "totals": totals}

@router.get("/daily")
async def daily(
    start: Optional[date] = Query(None),
    end: Optional[date] = Query(None),
):
    match: Dict[str, Any] = {}
    if start or end:
        d: Dict[str, Any] = {}
        if start: d["$gte"] = start
        if end:   d["$lte"] = end
        match["date"] = d

    try:
        coll = _get_collection()
        pipeline: List[Dict[str, Any]] = []
        if match:
            pipeline.append({"$match": match})
        pipeline += [
            {"$group": {"_id": "$date", "totalAmount": {"$sum": "$amount"}, "count": {"$sum": 1}}},
            {"$sort": {"_id": 1}},
        ]
        rows = await coll.aggregate(pipeline).to_list(length=3000)
        items = [{"date": r["_id"], "total": float(r.get("totalAmount", 0.0)), "count": int(r.get("count", 0))} for r in rows]
        return {"items": items}

    except Exception:
        # Fallback Python
        qry = Transaction.find(match) if match else Transaction.find_all()
        txs = await qry.to_list()
        bucket = defaultdict(lambda: {"total": 0.0, "count": 0})
        for t in txs:
            bucket[t.date]["total"] += float(t.amount or 0.0)
            bucket[t.date]["count"] += 1
        items = [{"date": d, "total": v["total"], "count": v["count"]} for d, v in sorted(bucket.items())]
        return {"items": items}

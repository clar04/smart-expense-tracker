from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from app.models.category import Category
from app.models.transaction import Transaction

router = APIRouter(prefix="/categories", tags=["categories"])

class CategoryIn(BaseModel):
    name: str

@router.get("")
async def list_categories():
    items = await Category.find_all().to_list()
    items.sort(key=lambda x: x.name.lower())
    return {"items": items}

@router.post("")
async def create_category(payload: CategoryIn):
    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Name is required")
    exists = await Category.find_one(Category.name == name)
    if exists:
        raise HTTPException(status_code=409, detail="Category already exists")
    saved = await Category(name=name).insert()
    return {"id": str(saved.id), "name": name}

@router.delete("/{category_id}")
async def delete_category(category_id: str, force: bool = Query(False, description="Set true to detach transactions then delete")):
    cat = await Category.get(category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")

    used = await Transaction.find(Transaction.category_id == category_id).count()
    if used > 0 and not force:
        raise HTTPException(status_code=400, detail=f"Category in use by {used} transactions. Use ?force=true to delete and detach.")

    if used > 0:
        txs = await Transaction.find(Transaction.category_id == category_id).to_list()
        for t in txs:
            t.category_id = None
            await t.save()

    await cat.delete()
    return {"deleted": True, "detached": used}

@router.get("/summary")
async def categories_summary():
    cats = await Category.find_all().to_list()
    result = []
    for c in cats:
        cnt = await Transaction.find(Transaction.category_id == str(c.id)).count()
        result.append({"id": str(c.id), "name": c.name, "count": cnt})
    return {"items": result}
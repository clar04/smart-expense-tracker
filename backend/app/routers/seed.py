from fastapi import APIRouter
from app.models.category import Category

router = APIRouter(prefix="/seed")

@router.post("/categories-default")
async def seed_categories_default():
    defaults = ["Food","Transport","Bills","Entertainment","Groceries","Other"]
    # upsert sederhana: cek ada atau belum (by name)
    inserted = 0
    for name in defaults:
        exists = await Category.find_one(Category.name == name)
        if not exists:
            await Category(name=name).insert()
            inserted += 1
    return {"ok": True, "inserted": inserted, "total_defaults": len(defaults)}

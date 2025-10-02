from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from .config import settings
from app.models.category import Category
from app.models.transaction import Transaction

async def init_db():
    client = AsyncIOMotorClient(settings.MONGO_URI)
    db = client[settings.MONGO_DB]
    await init_beanie(database=db, document_models=[Category, Transaction])

    try:
        await db["transactions"].create_index([("date", 1)])
        await db["transactions"].create_index([("created_at", -1)])
        await db["transactions"].create_index([("category_id", 1)])
        await db["transactions"].create_index(
            [("description", "text"), ("merchant", "text")],
            name="text_desc_merchant"
        )
    except Exception:
        pass

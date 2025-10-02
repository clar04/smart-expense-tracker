from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.db import init_db
from app.routers.health import router as health_router
from app.routers.seed import router as seed_router
from app.routers.transactions import router as transactions_router
from app.routers.categories import router as categories_router
from app.routers.labeling import router as labeling_router
from app.routers.report import router as report_router

app = FastAPI(title="Smart Expense Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    await init_db()

app.include_router(health_router)
app.include_router(seed_router)
app.include_router(transactions_router)
app.include_router(categories_router)
app.include_router(labeling_router)
app.include_router(report_router)
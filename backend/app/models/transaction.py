from beanie import Document
from pydantic import Field
from datetime import datetime, date
from typing import Optional

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

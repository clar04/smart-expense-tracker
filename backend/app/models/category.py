from beanie import Document
from pydantic import Field
from datetime import datetime
from typing import Optional

class Category(Document):
    name: str
    user_id: Optional[str] = None  # nanti bisa dipakai multi-user
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "categories"  # nama koleksi

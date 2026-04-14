from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, HttpUrl, Field


class ArticleCreate(BaseModel):
    title: str = Field(..., example="AI advances in 2026")
    content: str = Field(..., example="The full article text goes here.")
    source_url: Optional[HttpUrl] = Field(None, example="https://news.example.com/article")


class ArticleResponse(ArticleCreate):
    id: UUID
    created_at: datetime

    class Config:
        orm_mode = True

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, HttpUrl, Field, ConfigDict


class ArticleCreate(BaseModel):
    title: str = Field(..., json_schema_extra={"example": "AI advances in 2026"})
    content: str = Field(..., json_schema_extra={"example": "The full article text goes here."})
    category: Optional[str] = Field("General", json_schema_extra={"example": "Technology"})
    source_url: Optional[HttpUrl] = Field(None, json_schema_extra={"example": "https://news.example.com/article"})


class ArticleResponse(ArticleCreate):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

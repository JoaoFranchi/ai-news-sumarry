from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field


class SummaryResponse(BaseModel):
    id: UUID
    article_id: Optional[UUID]
    summary_text: str = Field(..., example="This article explains how AI summarization works.")
    created_at: datetime

    class Config:
        orm_mode = True


class SummarizeRequest(BaseModel):
    text: str = Field(..., example="Full article text to summarize.")
    article_id: Optional[UUID] = Field(None, example="a3f8f9c0-9d24-4b6a-8d75-a8f9b1234d56")


class SummarizeResponse(BaseModel):
    summary: str = Field(..., example="The article explains the latest AI news in three concise sentences.")
    key_points: List[str] = Field(..., example=["AI advances continue", "New product launch", "Market impact is growing"])
    summary_id: UUID

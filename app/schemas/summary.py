from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class SummaryResponse(BaseModel):
    id: UUID
    article_id: Optional[UUID]
    summary_text: str = Field(..., json_schema_extra={"example": "This article explains how AI summarization works."})
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SummarizeRequest(BaseModel):
    article_text: Optional[str] = Field(
        None,
        json_schema_extra={"example": "Full article text to summarize."},
    )
    # Backward-compatible field name for existing clients.
    text: Optional[str] = Field(
        None,
        json_schema_extra={"example": "Full article text to summarize."},
    )
    article_id: Optional[UUID] = Field(None, json_schema_extra={"example": "a3f8f9c0-9d24-4b6a-8d75-a8f9b1234d56"})
    length: Optional[str] = Field("medium", json_schema_extra={"example": "medium"})


class SummarizeResponse(BaseModel):
    summary: str = Field(..., json_schema_extra={"example": "The article explains the latest AI news in three concise sentences."})
    key_points: List[str] = Field(..., json_schema_extra={"example": ["AI advances continue", "New product launch", "Market impact is growing"]})
    summary_id: UUID

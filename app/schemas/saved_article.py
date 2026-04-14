from uuid import UUID
from pydantic import BaseModel, Field


class SavedArticleCreate(BaseModel):
    user_id: UUID = Field(..., example="4a6ffe28-b5fe-4da1-8e15-b295d1cc5cd7")
    article_id: UUID = Field(..., example="7e2cda9f-8c7a-4d15-b5b5-6221de4a37e8")


class SavedArticleResponse(SavedArticleCreate):
    id: UUID

    class Config:
        orm_mode = True

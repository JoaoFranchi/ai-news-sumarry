from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.saved_article import SavedArticle
from app.models.user import User
from app.schemas.saved_article import SavedArticleCreate, SavedArticleResponse
from app.services.auth_dependencies import get_current_user

router = APIRouter()


@router.post("/save", response_model=SavedArticleResponse, status_code=status.HTTP_201_CREATED)
def save_article(
    payload: SavedArticleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Save an article for a user."""
    if payload.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot save for another user")

    saved = SavedArticle(user_id=payload.user_id, article_id=payload.article_id)
    db.add(saved)
    db.commit()
    db.refresh(saved)
    return saved


@router.get("/saved/{user_id}", response_model=List[SavedArticleResponse])
def get_saved_articles(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List saved articles for a specific user."""
    if user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot view another user's saved articles")

    saved_list = db.scalars(select(SavedArticle).filter_by(user_id=user_id)).all()
    return saved_list


@router.delete("/save/{saved_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_saved_article(
    saved_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove a saved article entry."""
    saved_item = db.get(SavedArticle, saved_id)
    if not saved_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Saved article not found")
    if saved_item.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot delete another user's saved article")
    db.delete(saved_item)
    db.commit()
    return None

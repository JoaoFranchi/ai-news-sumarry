from uuid import UUID
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.article import Article
from app.models.user import User
from app.schemas.article import ArticleCreate, ArticleResponse
from app.services.article_content_service import hydrate_article_content_if_needed
from app.services.auth_dependencies import get_current_user

router = APIRouter()


@router.post("/articles", response_model=ArticleResponse, status_code=status.HTTP_201_CREATED)
def create_article(
    article_create: ArticleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new article record."""
    article = Article(
        title=article_create.title,
        content=article_create.content,
        category=article_create.category or "General",
        source_url=str(article_create.source_url) if article_create.source_url else None,
    )
    db.add(article)
    db.commit()
    db.refresh(article)
    return article


@router.get("/articles", response_model=List[ArticleResponse])
def list_articles(category: Optional[str] = None, db: Session = Depends(get_db)):
    """Return a list of all articles."""
    query = select(Article)
    if category:
        query = query.filter(Article.category == category)
    articles = db.scalars(query).all()
    return articles


@router.get("/articles/{article_id}", response_model=ArticleResponse)
def get_article(article_id: UUID, db: Session = Depends(get_db)):
    """Fetch an article by UUID."""
    article = db.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    return hydrate_article_content_if_needed(article, db)


@router.delete("/articles/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_article(
    article_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete an article by UUID."""
    article = db.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    db.delete(article)
    db.commit()
    return None

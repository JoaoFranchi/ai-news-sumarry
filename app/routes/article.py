from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.article import Article
from app.schemas.article import ArticleCreate, ArticleResponse

router = APIRouter()


@router.post("/articles", response_model=ArticleResponse, status_code=status.HTTP_201_CREATED)
def create_article(article_create: ArticleCreate, db: Session = Depends(get_db)):
    """Create a new article record."""
    article = Article(
        title=article_create.title,
        content=article_create.content,
        source_url=str(article_create.source_url) if article_create.source_url else None,
    )
    db.add(article)
    db.commit()
    db.refresh(article)
    return article


@router.get("/articles", response_model=List[ArticleResponse])
def list_articles(db: Session = Depends(get_db)):
    """Return a list of all articles."""
    articles = db.scalars(select(Article)).all()
    return articles


@router.get("/articles/{article_id}", response_model=ArticleResponse)
def get_article(article_id: UUID, db: Session = Depends(get_db)):
    """Fetch an article by UUID."""
    article = db.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    return article


@router.delete("/articles/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_article(article_id: UUID, db: Session = Depends(get_db)):
    """Delete an article by UUID."""
    article = db.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    db.delete(article)
    db.commit()
    return None

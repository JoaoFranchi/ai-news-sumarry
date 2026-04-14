from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.summary import Summary
from app.schemas.summary import SummaryResponse

router = APIRouter()


@router.get("/summaries", response_model=List[SummaryResponse])
def list_summaries(db: Session = Depends(get_db)):
    """Return all stored summaries."""
    summaries = db.scalars(select(Summary)).all()
    return summaries


@router.get("/summaries/{summary_id}", response_model=SummaryResponse)
def get_summary(summary_id: UUID, db: Session = Depends(get_db)):
    """Fetch a summary by UUID."""
    summary = db.get(Summary, summary_id)
    if not summary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Summary not found")
    return summary

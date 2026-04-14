from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.summary import Summary
from app.schemas.summary import SummarizeRequest, SummarizeResponse
from app.services.ai_service import summarize_text

router = APIRouter()


@router.post("/summarize", response_model=SummarizeResponse)
def summarize_article(request: SummarizeRequest, db: Session = Depends(get_db)):
    """Generate a summary and key points for the provided article text."""
    try:
        ai_result = summarize_text(request.text)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="AI service failed to summarize text.")

    saved_summary = Summary(article_id=request.article_id, summary_text=ai_result["summary"])
    db.add(saved_summary)
    db.commit()
    db.refresh(saved_summary)

    return {
        "summary": ai_result["summary"],
        "key_points": ai_result["key_points"],
        "summary_id": saved_summary.id,
    }

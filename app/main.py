from dotenv import load_dotenv

load_dotenv()

import os
from fastapi import FastAPI
from app.database import engine, Base
from app.routes import user, article, summary, ai, saved_article

app = FastAPI(title="AI News Summarizer")

# Create database tables automatically unless we are running tests.
if os.getenv("TESTING", "false").lower() != "true":
    Base.metadata.create_all(bind=engine)

# Include routers from each module
app.include_router(user, prefix="", tags=["users"])
app.include_router(article, prefix="", tags=["articles"])
app.include_router(summary, prefix="", tags=["summaries"])
app.include_router(ai, prefix="", tags=["ai"])
app.include_router(saved_article, prefix="", tags=["saved_articles"])

@app.get("/health")
def health_check():
    """Simple endpoint to verify the service is running."""
    return {"status": "ok", "service": "AI News Summarizer"}

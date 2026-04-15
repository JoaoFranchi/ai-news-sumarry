from dotenv import load_dotenv

load_dotenv()

import os
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.database import engine, Base
from app.routes import user, article, summary, ai, saved_article
from app.services.schema_updates import ensure_article_category_column

app = FastAPI(title="AI News Summarizer")

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables automatically unless we are running tests.
if os.getenv("TESTING", "false").lower() != "true":
    Base.metadata.create_all(bind=engine)
    ensure_article_category_column(engine)

# Include routers from each module
app.include_router(user, prefix="", tags=["users"])
app.include_router(article, prefix="", tags=["articles"])
app.include_router(summary, prefix="", tags=["summaries"])
app.include_router(ai, prefix="", tags=["ai"])
app.include_router(saved_article, prefix="", tags=["saved_articles"])


@app.exception_handler(RequestValidationError)
async def custom_validation_exception_handler(request: Request, exc: RequestValidationError):
    """Convert /register validation failures into clean HTTP 400 responses."""
    if request.url.path == "/register":
        for error in exc.errors():
            field = error.get("loc", [])[-1] if error.get("loc") else None

            # Enforce exact business messages requested for these constraints.
            if field == "name":
                return JSONResponse(status_code=400, content={"detail": "Name must be at most 20 characters long"})
            if field == "password":
                return JSONResponse(status_code=400, content={"detail": "Password must be at least 8 characters long"})

        # Keep response clean for other register validation errors (e.g. invalid email).
        first_message = exc.errors()[0].get("msg", "Invalid registration payload") if exc.errors() else "Invalid registration payload"
        return JSONResponse(status_code=400, content={"detail": first_message})

    # Preserve default validation semantics for non-register endpoints.
    return JSONResponse(status_code=422, content={"detail": exc.errors()})

@app.get("/health")
def health_check():
    """Simple endpoint to verify the service is running."""
    return {"status": "ok", "service": "AI News Summarizer"}

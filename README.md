# AI News Summarizer Backend

This project is a FastAPI backend for the "AI News Summarizer" application.
It is built with a clean modular architecture, SQLAlchemy ORM, PostgreSQL, and Pydantic validation.

## Quick Start

```bash
pip install -r requirements.txt
cp .env .env.local
# Edit .env.local with your DATABASE_URL and OPENAI_API_KEY

uvicorn app.main:app --reload
```

API available at `http://localhost:8000`

---

## Project Structure

- `app/main.py` - FastAPI application and router registration
- `app/database.py` - SQLAlchemy database engine and session dependency
- `app/models/` - ORM models for users, articles, summaries, and saved articles
- `app/schemas/` - Pydantic request and response models
- `app/routes/` - API route modules for user, article, summary, AI, and saved article endpoints
- `app/services/ai_service.py` - OpenAI integration for article summarization
- `tests/` - Unit and integration tests with pytest

## Requirements

- Python 3.11+ recommended
- PostgreSQL running locally or available via `DATABASE_URL`

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Create a PostgreSQL database named `ai_news_summary` or set `DATABASE_URL` in the `.env` file:

```bash
cp .env .env.local
# Update DATABASE_URL and OPENAI_API_KEY in .env.local
```

3. Run the application:

```bash
uvicorn app.main:app --reload
```

## Endpoints

- `POST /register`
- `POST /login`
- `GET /users/{id}`
- `POST /articles`
- `GET /articles`
- `GET /articles/{id}`
- `DELETE /articles/{id}`
- `GET /summaries`
- `GET /summaries/{id}`
- `POST /summarize`
- `POST /save`
- `GET /saved/{user_id}`
- `DELETE /save/{id}`

## Notes

- Passwords are hashed with `bcrypt`.
- The AI summarization endpoint returns a real OpenAI summary and stores it in the database.
- Tables are created automatically when the app starts.

## Testing

Run the test suite with:

```bash
pytest
```

See [DEVELOPMENT.md](DEVELOPMENT.md) for comprehensive testing and CI/CD documentation.

## CI/CD Pipeline

This project includes GitHub Actions workflows (`.github/workflows/tests.yml`) that:

- Automatically run tests on every `push` to `main` and on `pull_request`
- Use PostgreSQL 15 service container for testing
- Set environmental variables for secure testing
- Report test results and coverage

See [DEVELOPMENT.md](DEVELOPMENT.md) for detailed setup and contribution guidelines.

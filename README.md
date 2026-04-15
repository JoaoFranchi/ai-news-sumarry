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
- `GET /me` (JWT required)
- `GET /users/{id}`
- `POST /articles` (JWT required)
- `GET /articles`
- `GET /articles/{id}`
- `DELETE /articles/{id}` (JWT required)
- `GET /summaries`
- `GET /summaries/{id}`
- `POST /summarize`
- `POST /save` (JWT required)
- `GET /saved/{user_id}` (JWT required)
- `DELETE /save/{id}` (JWT required)
- `POST /news/fetch-random` - Fetch and save random articles from news sources

### Authentication

`POST /login` returns a bearer token:

```json
{
	"message": "Login successful",
	"user_id": "uuid",
	"token": {
		"access_token": "<jwt>",
		"token_type": "bearer"
	}
}
```

Use it in protected requests:

```http
Authorization: Bearer <jwt>
```

Set these values in `.env`:

```bash
JWT_SECRET_KEY=change_this_to_a_long_random_secret
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60
```

## Database Seeding

Use the seed script to preload sample data:

```bash
python seed.py
```

- Inserts sample articles up to a total of 100 records
- Uses categories like Politics, Sports, Technology, Economy
- Is idempotent (running again will not duplicate existing titles)

## News Fetching Feature

The application includes a news fetching feature that automatically retrieves articles from various news sources:

### Setup

1. Get a free API key from [NewsAPI.org](https://newsapi.org/)
2. Add your API key to the `.env` file:

```bash
NEWS_API_KEY=your_newsapi_key_here
```

### Usage

- **Frontend**: Click the "📰 Fetch 100 Random Articles" button in the web interface
- **API**: `POST /news/fetch-random` with optional `count` parameter (default: 100, max: 500)

The feature fetches articles from multiple categories (business, technology, science, health, sports, entertainment) to provide variety, cleans the data, and saves unique articles to your database.

### Notes

- Free NewsAPI accounts allow up to 100 requests per day
- Articles are deduplicated by title to avoid duplicates
- Content is truncated to 2000 characters for database storage
- Requires `NEWS_API_KEY` environment variable

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

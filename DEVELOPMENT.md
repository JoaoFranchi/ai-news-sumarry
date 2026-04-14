# Development & CI/CD Guide

## Local Development

### Prerequisites

- Python 3.11+
- PostgreSQL 15+ (or use SQLite for testing)
- Git

### Setup

1. **Clone the repository:**

```bash
git clone <repository_url>
cd ai_news_summary_2
```

2. **Create and activate a virtual environment:**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**

```bash
pip install -r requirements.txt
```

4. **Configure environment variables:**

```bash
cp .env .env.local
# Edit .env.local with your settings
```

Example `.env.local`:

```
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/ai_news_summary
OPENAI_API_KEY=sk-your-openai-key
```

5. **Run the application:**

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

---

## Testing

### Run all tests locally:

```bash
pytest
```

### Run specific test file:

```bash
pytest tests/test_users.py
```

### Run with coverage:

```bash
pip install pytest-cov
pytest --cov=app
```

### Run with verbose output:

```bash
pytest -v
```

---

## Continuous Integration (GitHub Actions)

The project includes an automated CI/CD pipeline (`.github/workflows/tests.yml`) that:

1. Triggers on `push` and `pull_request` to `main` branch
2. Spins up a PostgreSQL 15 service container
3. Installs dependencies
4. Configures test environment variables
5. Runs pytest with verbose output

### Workflow Steps

- **Checkout code:** Retrieves the repository
- **Set up Python:** Installs Python 3.11
- **Install dependencies:** Installs packages from `requirements.txt`
- **Set environment variables:**
  - `DATABASE_URL`: PostgreSQL connection string for tests
  - `OPENAI_API_KEY`: Dummy key for CI (no real API calls in tests)
  - `TESTING`: Flag to use SQLite in-memory DB during tests

### Making a CI/CD Pass

1. Push code to a branch
2. Create a pull request to `main`
3. GitHub Actions automatically runs tests
4. All tests must pass before merging to `main`

---

## Project Structure

```
├── app/
│   ├── main.py              # FastAPI app initialization
│   ├── database.py          # SQLAlchemy setup
│   ├── models/              # ORM models
│   ├── schemas/             # Pydantic request/response models
│   ├── routes/              # API route handlers
│   └── services/            # Business logic (AI integration)
├── tests/
│   ├── conftest.py          # pytest fixtures
│   ├── test_users.py        # User endpoint tests
│   ├── test_articles.py     # Article endpoint tests
│   └── test_summaries.py    # Summarization tests
├── .github/
│   └── workflows/
│       └── tests.yml        # CI/CD pipeline
├── .env                     # Environment variables (template)
├── .gitignore               # Git ignore patterns
├── requirements.txt         # Python dependencies
├── pytest.ini               # pytest configuration
└── README.md                # Project documentation
```

---

## Best Practices

### Code Quality

- Follow PEP 8 style guidelines
- Use type hints for functions
- Write docstrings for public functions
- Keep modules focused and modular

### Testing

- Write tests for new features
- Aim for ~70%+ code coverage
- Test both success and failure paths
- Use fixtures for test data

### Git Workflow

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Commit changes with meaningful messages
3. Push to branch: `git push origin feature/your-feature`
4. Create a Pull Request
5. Wait for CI/CD to pass
6. Merge to `main` after approval

---

## Deployment

### Docker (Optional)

Create a `Dockerfile` in the project root:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
docker build -t ai-news-summarizer .
docker run -p 8000:8000 ai-news-summarizer
```

### Production Considerations

- Use a production database (managed PostgreSQL)
- Enable HTTPS/TLS
- Add authentication/authorization
- Use environment-specific configs
- Enable logging and monitoring
- Rate limit API endpoints
- Use a production ASGI server (Gunicorn + Uvicorn)

---

## Troubleshooting

### Tests fail with "database connection refused"

Ensure PostgreSQL is running or the test is using SQLite (via `TESTING=true`).

### "OPENAI_API_KEY not found"

Set the environment variable locally or in `.env`:

```bash
export OPENAI_API_KEY=your_key_here
```

### Module imports fail

Ensure the virtual environment is activated:

```bash
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

---

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/en/20/)
- [Pytest Documentation](https://docs.pytest.org/)
- [GitHub Actions CI/CD](https://docs.github.com/en/actions)
- [OpenAI API](https://platform.openai.com/docs/)

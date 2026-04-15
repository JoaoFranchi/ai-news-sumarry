from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine


def ensure_article_category_column(engine: Engine) -> None:
    """Add articles.category if missing so existing DB files keep working."""
    inspector = inspect(engine)
    if "articles" not in inspector.get_table_names():
        return

    columns = {col["name"] for col in inspector.get_columns("articles")}
    if "category" in columns:
        return

    with engine.begin() as connection:
        connection.execute(text("ALTER TABLE articles ADD COLUMN category VARCHAR(60)"))
        connection.execute(text("UPDATE articles SET category = 'General' WHERE category IS NULL"))

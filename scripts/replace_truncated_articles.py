import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import httpx
from sqlalchemy import select

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.database import SessionLocal
from app.models.article import Article
from app.services.article_content_service import (
    fetch_full_article_text,
    has_sufficient_article_content,
    hydrate_article_content_if_needed,
)

TARGET_COUNT = 335

RSS_FEEDS = [
    ("World", "https://feeds.bbci.co.uk/news/world/rss.xml"),
    ("Business", "https://feeds.bbci.co.uk/news/business/rss.xml"),
    ("Technology", "https://feeds.bbci.co.uk/news/technology/rss.xml"),
    ("Science", "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml"),
    ("General", "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml"),
    ("World", "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"),
    ("Business", "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml"),
    ("Technology", "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml"),
    ("Science", "https://rss.nytimes.com/services/xml/rss/nyt/Science.xml"),
    ("General", "https://www.theguardian.com/world/rss"),
    ("Technology", "https://www.theguardian.com/uk/technology/rss"),
    ("Business", "https://www.theguardian.com/uk/business/rss"),
    ("General", "https://feeds.npr.org/1001/rss.xml"),
    ("Business", "https://feeds.npr.org/1006/rss.xml"),
    ("Technology", "https://feeds.npr.org/1019/rss.xml"),
    ("General", "https://www.aljazeera.com/xml/rss/all.xml"),
]

CATEGORY_MAP = {
    "technology": "Technology",
    "tech": "Technology",
    "business": "Business",
    "economy": "Economy",
    "science": "Science",
    "health": "Health",
    "sports": "Sports",
    "politics": "Politics",
    "world": "General",
}


def normalize_category(value: str | None, fallback: str) -> str:
    if not value:
        return fallback
    normalized = value.strip().lower()
    for key, mapped in CATEGORY_MAP.items():
        if key in normalized:
            return mapped
    return fallback or "General"


def clean_title(title: str) -> str:
    normalized = re.sub(r"\s+", " ", (title or "")).strip()
    return normalized[:255] if normalized else "Untitled Article"


def parse_feed(url: str):
    try:
        response = httpx.get(url, timeout=15.0, follow_redirects=True)
        response.raise_for_status()
        root = ET.fromstring(response.text)
    except Exception:
        return []

    items = []
    for item in root.findall(".//item"):
        title = item.findtext("title") or ""
        link = item.findtext("link") or ""
        category = item.findtext("category") or ""
        if link:
            items.append((title.strip(), link.strip(), category.strip()))
    return items


def main():
    session = SessionLocal()
    try:
        all_articles = session.scalars(select(Article)).all()
        start_count = len(all_articles)
        low_quality = [article for article in all_articles if not has_sufficient_article_content(article.content)]

        hydrated = 0
        for article in low_quality:
            before = article.content or ""
            updated = hydrate_article_content_if_needed(article, session)
            if has_sufficient_article_content(updated.content) and updated.content != before:
                hydrated += 1

        all_articles = session.scalars(select(Article)).all()
        low_quality = [article for article in all_articles if not has_sufficient_article_content(article.content)]

        removed = 0
        for article in low_quality:
            session.delete(article)
            removed += 1
        session.commit()

        current_articles = session.scalars(select(Article)).all()
        source_urls = {article.source_url for article in current_articles if article.source_url}
        titles = {article.title.strip().lower() for article in current_articles if article.title}

        added = 0
        for fallback_category, feed_url in RSS_FEEDS:
            if len(current_articles) + added >= TARGET_COUNT:
                break

            for raw_title, link, raw_category in parse_feed(feed_url):
                if len(current_articles) + added >= TARGET_COUNT:
                    break
                if not link or link in source_urls:
                    continue

                title = clean_title(raw_title)
                if title.strip().lower() in titles:
                    continue

                full_text = fetch_full_article_text(link)
                if not full_text or len(full_text) < 300:
                    continue

                category = normalize_category(raw_category, fallback_category)
                article = Article(
                    title=title,
                    content=full_text,
                    category=category,
                    source_url=link,
                )
                session.add(article)
                session.commit()
                session.refresh(article)

                added += 1
                source_urls.add(link)
                titles.add(title.strip().lower())

        final_articles = session.scalars(select(Article)).all()
        final_count = len(final_articles)
        remaining_low_quality = sum(1 for article in final_articles if not has_sufficient_article_content(article.content))

        print(
            f"REPLACE_DONE start={start_count} hydrated={hydrated} removed={removed} added={added} final={final_count} remaining_low_quality={remaining_low_quality}"
        )
    finally:
        session.close()


if __name__ == "__main__":
    main()
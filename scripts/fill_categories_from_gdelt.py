import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List

import httpx
from sqlalchemy import select

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.database import SessionLocal
from app.models.article import Article
from app.services.article_content_service import fetch_full_article_text, has_sufficient_article_content

TARGET = 90
TARGET_CATEGORIES = [
    "General",
    "Politics",
    "Sports",
    "Technology",
    "Economy",
    "Business",
    "Science",
    "Health",
    "Entertainment",
]

CATEGORY_QUERIES: Dict[str, List[str]] = {
    "General": [
        "global news",
        "international affairs",
        "current events",
    ],
    "Politics": [
        "politics government election parliament congress policy",
        "diplomacy sanctions legislation",
    ],
    "Sports": [
        "football basketball tennis olympics sports",
        "championship league match athlete",
    ],
    "Technology": [
        "technology ai cybersecurity software hardware",
        "startup cloud chips open source",
    ],
    "Economy": [
        "economy inflation unemployment gdp recession interest rates",
        "labor market central bank monetary policy",
        "economic growth consumer prices",
    ],
    "Business": [
        "business company earnings stocks market corporate",
        "merger acquisition industry retail finance",
    ],
    "Science": [
        "science research discovery nasa climate biology physics",
        "space mission study scientists",
    ],
    "Health": [
        "health medicine hospital disease vaccine public health",
        "mental health healthcare treatment",
    ],
    "Entertainment": [
        "entertainment film music television celebrity culture",
        "streaming hollywood festival concert",
    ],
}


def gdelt_article_urls(query: str, max_records: int = 250) -> List[dict]:
    url = "https://api.gdeltproject.org/api/v2/doc/doc"
    params = {
        "query": query,
        "mode": "ArtList",
        "maxrecords": str(max_records),
        "format": "json",
        "sort": "datedesc",
    }

    try:
        response = httpx.get(url, params=params, timeout=30.0, follow_redirects=True)
        response.raise_for_status()
        payload = response.json()
    except Exception:
        return []

    return payload.get("articles", []) if isinstance(payload, dict) else []


def main():
    session = SessionLocal()
    try:
        articles = session.scalars(select(Article)).all()
        counts = Counter((a.category or "General").strip().title() for a in articles)
        urls = {a.source_url for a in articles if a.source_url}
        titles = {a.title.strip().lower() for a in articles if a.title}

        print("BEFORE_GDELT")
        for category in TARGET_CATEGORIES:
            print(f"{category}={counts.get(category, 0)}")

        added = 0
        for category in TARGET_CATEGORIES:
            while counts.get(category, 0) < TARGET:
                progressed = False
                for query in CATEGORY_QUERIES.get(category, []):
                    if counts.get(category, 0) >= TARGET:
                        break

                    candidates = gdelt_article_urls(query, max_records=250)
                    for item in candidates:
                        if counts.get(category, 0) >= TARGET:
                            break

                        link = (item.get("url") or "").strip()
                        title = (item.get("title") or "").strip()[:255]
                        if not link or not title:
                            continue
                        if link in urls or title.lower() in titles:
                            continue

                        full_text = fetch_full_article_text(link)
                        if not has_sufficient_article_content(full_text):
                            continue

                        article = Article(
                            title=title,
                            content=full_text,
                            category=category,
                            source_url=link,
                        )
                        session.add(article)
                        session.commit()
                        session.refresh(article)

                        urls.add(link)
                        titles.add(title.lower())
                        counts[category] += 1
                        added += 1
                        progressed = True
                        print(f"ADDED category={category} now={counts[category]} title={title[:60]!r}")

                if not progressed:
                    break

        print(f"GDELT_ADDED_TOTAL={added}")
        final = session.scalars(select(Article)).all()
        final_counts = Counter((a.category or "General").strip().title() for a in final)

        print("AFTER_GDELT")
        for category in TARGET_CATEGORIES:
            print(f"{category}={final_counts.get(category, 0)}")
        print(f"FINAL_TOTAL={len(final)}")
    finally:
        session.close()


if __name__ == "__main__":
    main()

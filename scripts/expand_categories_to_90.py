import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple

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

CATEGORY_FEEDS: Dict[str, List[str]] = {
    "General": [
        "https://feeds.bbci.co.uk/news/world/rss.xml",
        "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
        "https://feeds.npr.org/1001/rss.xml",
        "https://www.aljazeera.com/xml/rss/all.xml",
        "https://www.theguardian.com/world/rss",
    ],
    "Politics": [
        "https://feeds.bbci.co.uk/news/politics/rss.xml",
        "https://rss.nytimes.com/services/xml/rss/nyt/Politics.xml",
        "https://www.theguardian.com/politics/rss",
        "https://feeds.npr.org/1014/rss.xml",
    ],
    "Sports": [
        "https://feeds.bbci.co.uk/sport/rss.xml",
        "https://rss.nytimes.com/services/xml/rss/nyt/Sports.xml",
        "https://www.theguardian.com/uk/sport/rss",
        "https://www.espn.com/espn/rss/news",
    ],
    "Technology": [
        "https://feeds.bbci.co.uk/news/technology/rss.xml",
        "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",
        "https://www.theguardian.com/uk/technology/rss",
        "https://feeds.arstechnica.com/arstechnica/technology-lab",
    ],
    "Economy": [
        "https://rss.nytimes.com/services/xml/rss/nyt/Economy.xml",
        "https://www.theguardian.com/business/economics/rss",
        "https://www.cnbc.com/id/100003114/device/rss/rss.html",
        "https://www.ft.com/rss/home/us",
        "https://feeds.npr.org/1006/rss.xml",
    ],
    "Business": [
        "https://feeds.bbci.co.uk/news/business/rss.xml",
        "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml",
        "https://www.theguardian.com/uk/business/rss",
        "https://feeds.npr.org/1006/rss.xml",
        "https://www.cnbc.com/id/10001147/device/rss/rss.html",
    ],
    "Science": [
        "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml",
        "https://rss.nytimes.com/services/xml/rss/nyt/Science.xml",
        "https://www.theguardian.com/science/rss",
        "https://www.nasa.gov/rss/dyn/breaking_news.rss",
    ],
    "Health": [
        "https://feeds.bbci.co.uk/news/health/rss.xml",
        "https://rss.nytimes.com/services/xml/rss/nyt/Health.xml",
        "https://www.theguardian.com/society/health/rss",
        "https://www.who.int/feeds/entity/mediacentre/news/en/rss.xml",
    ],
    "Entertainment": [
        "https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml",
        "https://rss.nytimes.com/services/xml/rss/nyt/Arts.xml",
        "https://www.theguardian.com/uk/culture/rss",
        "https://variety.com/feed/",
    ],
}

ECONOMY_KEYWORDS = {
    "economy", "economic", "inflation", "gdp", "fed", "interest rate", "recession", "jobs", "labor", "unemployment",
}


def clean_title(title: str) -> str:
    cleaned = re.sub(r"\s+", " ", (title or "")).strip()
    return cleaned[:255] if cleaned else "Untitled Article"


def parse_feed(url: str) -> List[Tuple[str, str, str]]:
    try:
        response = httpx.get(url, timeout=20.0, follow_redirects=True)
        response.raise_for_status()
        root = ET.fromstring(response.text)
    except Exception:
        return []

    items: List[Tuple[str, str, str]] = []
    for item in root.findall(".//item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        category = (item.findtext("category") or "").strip()
        if title and link:
            items.append((title, link, category))
    return items


def should_use_for_economy(title: str, raw_category: str) -> bool:
    text = f"{title} {raw_category}".lower()
    return any(keyword in text for keyword in ECONOMY_KEYWORDS)


def main():
    session = SessionLocal()
    try:
        articles = session.scalars(select(Article)).all()
        counts = Counter((a.category or "General").strip().title() for a in articles)
        source_urls = {a.source_url for a in articles if a.source_url}
        titles = {a.title.strip().lower() for a in articles if a.title}

        print("BEFORE_COUNTS")
        for category in TARGET_CATEGORIES:
            print(f"{category}={counts.get(category, 0)}")

        feed_candidates: Dict[str, List[Tuple[str, str, str]]] = {category: [] for category in TARGET_CATEGORIES}
        for category, feeds in CATEGORY_FEEDS.items():
            seen_links = set()
            for feed in feeds:
                for title, link, raw_cat in parse_feed(feed):
                    if link in seen_links:
                        continue
                    seen_links.add(link)
                    feed_candidates[category].append((title, link, raw_cat))

        indices = {category: 0 for category in TARGET_CATEGORIES}
        added = 0
        attempts = 0
        max_attempts = 20000

        while attempts < max_attempts:
            missing = [c for c in TARGET_CATEGORIES if counts.get(c, 0) < TARGET]
            if not missing:
                break

            progress_this_cycle = False
            for category in missing:
                candidates = feed_candidates.get(category, [])
                while indices[category] < len(candidates) and counts.get(category, 0) < TARGET:
                    attempts += 1
                    title, link, raw_cat = candidates[indices[category]]
                    indices[category] += 1

                    if link in source_urls:
                        continue

                    cleaned_title = clean_title(title)
                    if cleaned_title.strip().lower() in titles:
                        continue

                    if category == "Economy" and not should_use_for_economy(cleaned_title, raw_cat):
                        continue

                    full_text = fetch_full_article_text(link)
                    if not has_sufficient_article_content(full_text):
                        continue

                    article = Article(
                        title=cleaned_title,
                        content=full_text,
                        category=category,
                        source_url=link,
                    )
                    session.add(article)
                    session.commit()
                    session.refresh(article)

                    source_urls.add(link)
                    titles.add(cleaned_title.strip().lower())
                    counts[category] += 1
                    added += 1
                    progress_this_cycle = True
                    print(f"ADDED category={category} now={counts[category]} title={cleaned_title[:60]!r}")
                    break

            if not progress_this_cycle:
                break

        print(f"ADDED_TOTAL={added}")
        print("AFTER_COUNTS")
        final_articles = session.scalars(select(Article)).all()
        final_counts = Counter((a.category or "General").strip().title() for a in final_articles)
        for category in TARGET_CATEGORIES:
            print(f"{category}={final_counts.get(category, 0)}")
        print(f"FINAL_TOTAL={len(final_articles)}")
    finally:
        session.close()


if __name__ == "__main__":
    main()

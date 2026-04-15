import re
from html import unescape
from typing import Optional

import httpx
from sqlalchemy.orm import Session
import trafilatura

from app.models.article import Article

TRUNCATED_NEWSAPI_PATTERN = re.compile(r"\[\+\d+\s+chars\]\s*$", re.IGNORECASE)
MIN_FULL_ARTICLE_WORDS = 120
MIN_FULL_ARTICLE_CHARS = 800


def is_probably_truncated_content(content: str | None) -> bool:
    if not content:
        return False
    normalized = content.strip()
    if TRUNCATED_NEWSAPI_PATTERN.search(normalized):
        return True
    return normalized.endswith("...") and len(normalized) < 600


def has_sufficient_article_content(content: str | None) -> bool:
    if not content:
        return False
    normalized = content.strip()
    if not normalized:
        return False
    if is_probably_truncated_content(normalized):
        return False
    word_count = len(normalized.split())
    return word_count >= MIN_FULL_ARTICLE_WORDS or len(normalized) >= MIN_FULL_ARTICLE_CHARS


def _clean_text(value: str) -> str:
    text = unescape(value)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _strip_html_noise(html: str) -> str:
    cleaned = re.sub(r"(?is)<script[^>]*>.*?</script>", " ", html)
    cleaned = re.sub(r"(?is)<style[^>]*>.*?</style>", " ", cleaned)
    return cleaned


def extract_article_text_from_html(html: str) -> str:
    cleaned_html = _strip_html_noise(html)

    article_blocks = re.findall(r"(?is)<article[^>]*>(.*?)</article>", cleaned_html)
    search_blocks = article_blocks if article_blocks else [cleaned_html]

    paragraphs: list[str] = []
    for block in search_blocks:
        for paragraph in re.findall(r"(?is)<p[^>]*>(.*?)</p>", block):
            text = _clean_text(re.sub(r"(?is)<[^>]+>", " ", paragraph))
            if len(text) >= 40:
                paragraphs.append(text)

    unique_paragraphs: list[str] = []
    seen: set[str] = set()
    for paragraph in paragraphs:
        key = paragraph.lower()
        if key not in seen:
            seen.add(key)
            unique_paragraphs.append(paragraph)

    return "\n\n".join(unique_paragraphs)


def fetch_full_article_text(source_url: str) -> Optional[str]:
    if not source_url:
        return None

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }

    try:
        response = httpx.get(source_url, timeout=12.0, follow_redirects=True, headers=headers)
        response.raise_for_status()
        extracted = trafilatura.extract(
            response.text,
            url=source_url,
            include_comments=False,
            include_tables=False,
            favor_precision=True,
        )
        candidates = []
        if extracted:
            candidates.append(_clean_text(extracted))
        fallback_text = extract_article_text_from_html(response.text)
        if fallback_text:
            candidates.append(fallback_text)

        best_text = None
        best_words = -1
        for candidate in candidates:
            words = len(candidate.split())
            if words > best_words:
                best_text = candidate
                best_words = words

        if has_sufficient_article_content(best_text):
            return best_text
        return None
    except Exception:
        return None


def hydrate_article_content_if_needed(article: Article, db: Session) -> Article:
    if not article or not article.source_url:
        return article

    if has_sufficient_article_content(article.content):
        return article

    full_text = fetch_full_article_text(article.source_url)
    if not full_text:
        return article

    if len(full_text) <= len(article.content or ""):
        return article

    article.content = full_text
    db.add(article)
    db.commit()
    db.refresh(article)
    return article

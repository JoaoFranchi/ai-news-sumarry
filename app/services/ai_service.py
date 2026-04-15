import json
import os
from typing import List

import openai
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MAX_INPUT_CHARS = 12000
MIN_SUMMARIZABLE_WORDS = 30
SHORT_ARTICLE_MESSAGE = "Article too short to summarize effectively"
VALID_SUMMARY_LENGTHS = {"short", "medium", "long"}
SUMMARY_PROMPTS = {
    "short": "Summarize this news article in 1-2 concise sentences.",
    "medium": "Summarize this news article in 3-4 clear and informative sentences.",
    "long": "Provide a detailed summary of this news article in 5-7 sentences, explaining key events and context.",
}
SUMMARY_SENTENCE_LIMITS = {"short": 2, "medium": 4, "long": 7}
KEY_POINT_LIMITS = {"short": 2, "medium": 4, "long": 5}
MAX_TOKENS_BY_LENGTH = {"short": 250, "medium": 500, "long": 800}

# Keep compatibility with both legacy and new OpenAI SDK usage.
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY


def _is_placeholder_key(api_key: str | None) -> bool:
    if not api_key:
        return True
    normalized = api_key.strip().lower()
    return normalized in {"your_openai_api_key_here", "changeme", "replace_me"}


def _clean_input_text(text: str) -> str:
    """Normalize whitespace and clip very long content before AI call."""
    cleaned = " ".join(text.strip().split())
    if len(cleaned) > MAX_INPUT_CHARS:
        cleaned = cleaned[:MAX_INPUT_CHARS].rstrip()
    return cleaned


def _is_too_short(text: str) -> bool:
    return len(text.split()) < MIN_SUMMARIZABLE_WORDS


def _normalize_length(length: str | None) -> str:
    normalized = (length or "medium").strip().lower()
    if normalized not in VALID_SUMMARY_LENGTHS:
        raise ValueError("length must be one of: short, medium, long")
    return normalized


def _truncate_at_word_boundary(text: str, max_length: int = 120) -> str:
    """Truncate text without cutting words in half."""
    normalized = " ".join(text.split()).strip()
    if len(normalized) <= max_length:
        return normalized

    # Leave room for ellipsis when truncating.
    candidate = normalized[: max_length - 3].rstrip()
    last_space = candidate.rfind(" ")
    if last_space > 0:
        candidate = candidate[:last_space].rstrip()

    if not candidate:
        candidate = normalized[: max_length - 3].rstrip()

    return f"{candidate}..."


def _fallback_summary(text: str, length: str = "medium") -> dict:
    """Generate a basic local summary when external AI is unavailable."""
    normalized_length = _normalize_length(length)
    clean_text = _clean_input_text(text)
    if not clean_text:
        raise ValueError("Text to summarize must not be empty.")

    if _is_too_short(clean_text):
        return {"summary": SHORT_ARTICLE_MESSAGE, "key_points": []}

    # Small heuristic summarizer aligned with requested summary length.
    sentences = [part.strip() for part in clean_text.replace("?", ".").replace("!", ".").split(".") if part.strip()]
    sentence_limit = SUMMARY_SENTENCE_LIMITS[normalized_length]
    summary_sentences = sentences[:sentence_limit] if sentences else [clean_text[:240]]
    summary = ". ".join(summary_sentences).strip()
    if summary and not summary.endswith("."):
        summary += "."

    key_points: List[str] = []
    point_limit = KEY_POINT_LIMITS[normalized_length]
    for sentence in summary_sentences[:point_limit]:
        trimmed = sentence.strip()
        if trimmed:
            key_points.append(_truncate_at_word_boundary(trimmed, 120))

    if not key_points:
        key_points = [_truncate_at_word_boundary(clean_text, 120)]

    return {"summary": summary, "key_points": key_points}


def _parse_ai_response(content: str, length: str = "medium") -> dict:
    """Parse the OpenAI response to extract summary and key points."""
    normalized_length = _normalize_length(length)
    try:
        payload = json.loads(content)
        summary = payload.get("summary", "")
        key_points = payload.get("key_points", [])
    except json.JSONDecodeError:
        summary = content.strip()
        key_points = [line.strip("- ").strip() for line in content.splitlines() if line.strip().startswith("-")]

    if not isinstance(key_points, list):
        key_points = [str(key_points)]

    summary = str(summary).strip()
    key_points = [str(point).strip() for point in key_points if str(point).strip()]

    if not summary:
        summary = SHORT_ARTICLE_MESSAGE

    # Keep output concise and presentation-friendly.
    key_points = [_truncate_at_word_boundary(point, 120) for point in key_points]
    if len(key_points) > KEY_POINT_LIMITS[normalized_length]:
        key_points = key_points[: KEY_POINT_LIMITS[normalized_length]]

    return {
        "summary": summary,
        "key_points": key_points,
    }


def summarize_text(text: str, length: str = "medium") -> dict:
    """Generate a short news summary using the OpenAI API."""
    if not text or not text.strip():
        raise ValueError("Text to summarize must not be empty.")

    normalized_length = _normalize_length(length)
    cleaned_text = _clean_input_text(text)

    if _is_too_short(cleaned_text):
        return {"summary": SHORT_ARTICLE_MESSAGE, "key_points": []}

    # If key is missing/placeholder, keep the feature working with local fallback.
    if _is_placeholder_key(OPENAI_API_KEY):
        return _fallback_summary(cleaned_text, normalized_length)

    prompt = (
        f"{SUMMARY_PROMPTS[normalized_length]}\n"
        "Then provide key points as short bullets with factual highlights.\n"
        "Return your answer as valid JSON with this exact structure:\n"
        '{"summary":"...","key_points":["...","..."]}\n\n'
        f"Article:\n{cleaned_text}"
    )

    try:
        # New OpenAI SDK style (v1+).
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert news editor producing factual, structured summaries."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=MAX_TOKENS_BY_LENGTH[normalized_length],
            response_format={"type": "json_object"},
        )
        content = (response.choices[0].message.content or "").strip()
        if not content:
            return _fallback_summary(cleaned_text, normalized_length)
        return _parse_ai_response(content, normalized_length)
    except Exception:
        # If the external AI call fails (invalid key/network/rate limit), fallback locally.
        return _fallback_summary(cleaned_text, normalized_length)

import json
import os
from typing import List

import openai
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required for AI summarization.")

openai.api_key = OPENAI_API_KEY


def _parse_ai_response(content: str) -> dict:
    """Parse the OpenAI response to extract summary and key points."""
    try:
        payload = json.loads(content)
        summary = payload.get("summary", "")
        key_points = payload.get("key_points", [])
    except json.JSONDecodeError:
        summary = content.strip()
        key_points = [line.strip("- ").strip() for line in content.splitlines() if line.strip().startswith("-")]

    if not isinstance(key_points, list):
        key_points = [str(key_points)]

    return {
        "summary": summary,
        "key_points": key_points,
    }


def summarize_text(text: str) -> dict:
    """Generate a short news summary using the OpenAI API."""
    if not text or not text.strip():
        raise ValueError("Text to summarize must not be empty.")

    prompt = (
        "Summarize this news article in 3 concise sentences focusing on key facts. "
        "Return a JSON object with keys 'summary' and 'key_points'. "
        "'key_points' should be a list of 3 bullet points.\n\n"
        f"Article:\n{text.strip()}"
    )

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a concise news summarization assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        max_tokens=250,
    )

    content = response.choices[0].message["content"].strip()
    return _parse_ai_response(content)

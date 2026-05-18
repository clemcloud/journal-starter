import json
import re

from openai import AsyncOpenAI

from api.config import get_settings


def _default_client() -> AsyncOpenAI:
    settings = get_settings()
    return AsyncOpenAI(
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
    )


def _extract_json(text: str) -> dict:
    """
    Safely extract JSON even if model returns extra text.
    """
    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to extract JSON block from messy response
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return json.loads(match.group())

    raise ValueError(f"Invalid JSON from LLM: {text}")


async def analyze_journal_entry(
    entry_id: str,
    entry_text: str,
    client: AsyncOpenAI | None = None,
) -> dict:
    if client is None:
        client = _default_client()

    response = await client.chat.completions.create(
        model=get_settings().openai_model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a strict JSON generator. "
                    "Return ONLY valid JSON. No explanations. No markdown. No extra text."
                ),
            },
            {
                "role": "user",
                "content": f"""
Analyze this journal entry and return ONLY valid JSON.

Text:
{entry_text}

Format:
{{
  "sentiment": "positive | negative | neutral",
  "summary": "short summary",
  "topics": ["topic1", "topic2"]
}}
""",
            },
        ],
    )

    content = response.choices[0].message.content

    if not content:
        raise ValueError("LLM returned empty response")

    result = _extract_json(content)

    return {
        "entry_id": entry_id,
        "sentiment": result.get("sentiment", "neutral"),
        "summary": result.get("summary", ""),
        "topics": result.get("topics", []),
    }

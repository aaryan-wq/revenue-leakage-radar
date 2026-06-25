import json
import logging
from typing import Any

import httpx

from core.config import settings

logger = logging.getLogger(__name__)


class AIProviderError(Exception):
    pass


def call_openai_json(system_prompt: str, user_prompt: str) -> dict[str, Any]:
    if not settings.openai_api_key:
        raise AIProviderError("OpenAI API key not configured")

    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.openai_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.openai_model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "response_format": {"type": "json_object"},
                    "temperature": 0,
                },
            )
            response.raise_for_status()
            payload = response.json()
            content = payload["choices"][0]["message"]["content"]
            return json.loads(content)
    except (httpx.HTTPError, KeyError, json.JSONDecodeError) as exc:
        logger.warning("OpenAI call failed: %s", exc)
        raise AIProviderError("AI request failed") from exc

"""DeepSeek LLM provider (OpenAI-compatible API)."""
from __future__ import annotations

import logging

from recipe.llm import LlmProvider, register
from recipe.config import get_api_key

log = logging.getLogger(__name__)


@register("deepseek")
class DeepSeekProvider(LlmProvider):
    """DeepSeek (OpenAI-compatible API)"""

    BASE_URL = "https://api.deepseek.com/v1"
    MODEL = "deepseek-chat"

    def __init__(self, **kwargs):
        self.api_key = get_api_key("DEEPSEEK_API_KEY")

    def chat(self, system_prompt: str, user_message: str) -> str:
        import httpx

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "temperature": 0.3,
        }

        log.debug("Sending request to DeepSeek (%s)", self.MODEL)
        resp = httpx.post(
            f"{self.BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=120,
        )
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        log.debug("DeepSeek response length: %d chars", len(content))
        return content

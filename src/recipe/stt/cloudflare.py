"""Cloudflare Workers AI Speech-to-Text."""
from __future__ import annotations

import logging
from pathlib import Path

from recipe.stt import SttEngine, register
from recipe.config import get_api_key

log = logging.getLogger(__name__)


@register("cloudflare")
class CloudflareSttEngine(SttEngine):
    """Cloudflare Workers AI REST API"""

    def __init__(self, **kwargs):
        self.account_id = get_api_key("CLOUDFLARE_ACCOUNT_ID")
        self.api_token = get_api_key("CLOUDFLARE_API_TOKEN")

    def transcribe(self, audio_path: Path, language: str = "zh") -> str:
        import httpx

        url = (
            f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}"
            f"/ai/run/@cf/openai/whisper"
        )
        headers = {"Authorization": f"Bearer {self.api_token}"}

        audio_data = audio_path.read_bytes()
        log.debug("Uploading %d bytes to Cloudflare Workers AI", len(audio_data))

        resp = httpx.post(
            url,
            headers=headers,
            content=audio_data,
            timeout=300,
        )
        resp.raise_for_status()
        result = resp.json()
        text = result.get("result", {}).get("text", "")
        log.debug("Cloudflare transcription length: %d chars", len(text))
        return text

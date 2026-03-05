"""Bytedance Volcano Engine (bigmodel flash) STT."""
from __future__ import annotations

import base64
import logging
import uuid
from pathlib import Path

import httpx

from recipe.config import get_api_key
from recipe.stt import SttEngine, register

log = logging.getLogger(__name__)

API_URL = "https://openspeech.bytedance.com/api/v3/auc/bigmodel/recognize/flash"
RESOURCE_ID = "volc.bigasr.auc_turbo"


@register("volcano")
class VolcanoSttEngine(SttEngine):
    """Bytedance Volcano Engine (flash bigmodel ASR)"""

    def __init__(self, **kwargs):
        self.app_key = get_api_key("VOLCANO_APP_KEY")
        self.access_key = get_api_key("VOLCANO_ACCESS_KEY")

    def transcribe(self, audio_path: Path, language: str = "zh") -> str:
        audio_data = audio_path.read_bytes()
        audio_b64 = base64.b64encode(audio_data).decode("utf-8")
        log.debug("Sending %d bytes (%d base64) to Volcano Engine", len(audio_data), len(audio_b64))

        request_id = str(uuid.uuid4())
        headers = {
            "X-Api-App-Key": self.app_key,
            "X-Api-Access-Key": self.access_key,
            "X-Api-Resource-Id": RESOURCE_ID,
            "X-Api-Request-Id": request_id,
            "X-Api-Sequence": "-1",
        }

        payload = {
            "user": {"uid": self.app_key},
            "audio": {"data": audio_b64},
            "request": {"model_name": "bigmodel"},
        }

        # Use HTTP/1.1 to avoid potential HTTP/2 gateway issues
        with httpx.Client(http2=False, timeout=300) as client:
            resp = client.post(API_URL, json=payload, headers=headers)

        status_code = resp.headers.get("X-Api-Status-Code", "")
        message = resp.headers.get("X-Api-Message", "")
        log.debug("Volcano status=%s message=%s", status_code, message)

        if status_code != "20000000":
            raise RuntimeError(
                f"Volcano Engine ASR failed: status={status_code}, message={message}"
            )

        data = resp.json()
        log.debug("Volcano response keys: %s", list(data.keys()))

        # Extract text from result utterances
        result = data.get("result", {})
        text_parts = []
        for utterance in result.get("utterances", []):
            t = utterance.get("text", "")
            if t:
                text_parts.append(t)

        # Fallback: some responses put text directly in result
        if not text_parts and "text" in result:
            text_parts.append(result["text"])

        text = "".join(text_parts)
        log.debug("Volcano transcription length: %d chars", len(text))
        return text

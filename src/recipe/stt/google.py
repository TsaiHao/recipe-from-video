"""Google Cloud Speech-to-Text."""
from __future__ import annotations

import logging
from pathlib import Path

from recipe.stt import SttEngine, register

log = logging.getLogger(__name__)


@register("google")
class GoogleSttEngine(SttEngine):
    """Google Cloud Speech-to-Text (requires google-cloud-speech)"""

    def __init__(self, **kwargs):
        try:
            from google.cloud import speech  # noqa: F401
        except ImportError:
            raise RuntimeError("Install the 'google' extra: uv pip install 'recipe[google]'")

    def transcribe(self, audio_path: Path, language: str = "zh") -> str:
        from google.cloud import speech

        client = speech.SpeechClient()

        lang_map = {"zh": "zh-CN", "en": "en-US", "ja": "ja-JP"}
        lang_code = lang_map.get(language, language)

        audio_data = audio_path.read_bytes()
        log.debug("Sending %d bytes to Google Speech-to-Text", len(audio_data))

        audio = speech.RecognitionAudio(content=audio_data)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code=lang_code,
        )

        response = client.recognize(config=config, audio=audio)
        text = " ".join(
            result.alternatives[0].transcript
            for result in response.results
            if result.alternatives
        )
        log.debug("Google transcription length: %d chars", len(text))
        return text

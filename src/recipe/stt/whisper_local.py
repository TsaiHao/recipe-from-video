"""Local Whisper transcription using faster-whisper (CTranslate2)."""
from __future__ import annotations

import logging
from pathlib import Path

from recipe.stt import SttEngine, register

log = logging.getLogger(__name__)


@register("whisper-local")
class WhisperLocalEngine(SttEngine):
    """Local faster-whisper (CTranslate2-based)"""

    def __init__(self, model_size: str = "large-v3", **kwargs):
        self.model_size = model_size
        self._model = None

    def _load_model(self):
        if self._model is None:
            from faster_whisper import WhisperModel
            log.debug("Loading whisper model: %s", self.model_size)
            self._model = WhisperModel(self.model_size, compute_type="auto")
        return self._model

    def transcribe(self, audio_path: Path, language: str = "zh") -> str:
        model = self._load_model()
        log.debug("Transcribing: %s", audio_path)
        segments, info = model.transcribe(str(audio_path), language=language)
        text = "".join(seg.text for seg in segments)
        log.debug("Transcription length: %d chars, detected language: %s (prob=%.2f)",
                   len(text), info.language, info.language_probability)
        return text

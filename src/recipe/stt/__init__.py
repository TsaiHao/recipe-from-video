from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path


class SttEngine(ABC):
    @abstractmethod
    def transcribe(self, audio_path: Path, language: str = "zh") -> str:
        ...


# Registry populated by imports below
STT_BACKENDS: dict[str, type[SttEngine]] = {}


def register(name: str):
    """Decorator to register an STT backend."""
    def decorator(cls: type[SttEngine]) -> type[SttEngine]:
        STT_BACKENDS[name] = cls
        return cls
    return decorator


def create_stt_engine(name: str, **kwargs) -> SttEngine:
    """Instantiate an STT engine by name."""
    if name not in STT_BACKENDS:
        available = ", ".join(STT_BACKENDS)
        raise ValueError(f"Unknown STT backend: {name!r}. Available: {available}")
    return STT_BACKENDS[name](**kwargs)


# Import backends to trigger registration
from recipe.stt.whisper_local import WhisperLocalEngine  # noqa: E402, F401
from recipe.stt.cloudflare import CloudflareSttEngine  # noqa: E402, F401
from recipe.stt.aws import AwsSttEngine  # noqa: E402, F401
from recipe.stt.google import GoogleSttEngine  # noqa: E402, F401
from recipe.stt.volcano import VolcanoSttEngine  # noqa: E402, F401

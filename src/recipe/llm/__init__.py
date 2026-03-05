from __future__ import annotations

from abc import ABC, abstractmethod


class LlmProvider(ABC):
    @abstractmethod
    def chat(self, system_prompt: str, user_message: str) -> str:
        ...


# Registry populated by imports below
LLM_BACKENDS: dict[str, type[LlmProvider]] = {}


def register(name: str):
    """Decorator to register an LLM backend."""
    def decorator(cls: type[LlmProvider]) -> type[LlmProvider]:
        LLM_BACKENDS[name] = cls
        return cls
    return decorator


def create_llm_provider(name: str, **kwargs) -> LlmProvider:
    """Instantiate an LLM provider by name."""
    if name not in LLM_BACKENDS:
        available = ", ".join(LLM_BACKENDS)
        raise ValueError(f"Unknown LLM provider: {name!r}. Available: {available}")
    return LLM_BACKENDS[name](**kwargs)


# Import backends to trigger registration
from recipe.llm.deepseek import DeepSeekProvider  # noqa: E402, F401

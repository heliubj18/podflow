from __future__ import annotations
from abc import ABC, abstractmethod

class BaseLLM(ABC):
    @abstractmethod
    async def chat(self, messages: list[dict[str, str]], temperature: float = 0.7, max_tokens: int = 4000) -> str:
        """Send messages and return generated text."""

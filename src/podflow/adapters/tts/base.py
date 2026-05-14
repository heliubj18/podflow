from __future__ import annotations
from abc import ABC, abstractmethod


class BaseTTS(ABC):
    @abstractmethod
    async def synthesize(self, text: str, voice: str) -> bytes:
        """Convert text to speech, return WAV bytes."""

    @abstractmethod
    def list_voices(self) -> list[dict[str, str]]:
        """Return available voices as [{"id": ..., "name": ...}]."""

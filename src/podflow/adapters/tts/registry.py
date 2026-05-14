from __future__ import annotations
from podflow.adapters.tts.base import BaseTTS
from podflow.config import TTSConfig


def create_tts(config: TTSConfig) -> BaseTTS:
    if config.provider == "edge-tts":
        from podflow.adapters.tts.edge import EdgeTTS
        return EdgeTTS()
    raise ValueError(f"Unknown TTS provider: {config.provider}")

from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field


class LLMConfig(BaseModel):
    provider: str = "ollama"
    base_url: str = "http://localhost:11434/v1"
    api_key: str = ""
    model: str = "qwen3:27b"
    temperature: float = 0.7
    max_tokens: int = 4000


class TTSConfig(BaseModel):
    provider: str = "edge-tts"
    voice: str = "zh-CN-XiaoxiaoNeural"
    host_voice: str = "zh-CN-YunxiNeural"
    guest_voice: str = "zh-CN-XiaoxiaoNeural"


class OCRConfig(BaseModel):
    enabled: Literal["auto", "on", "off"] = "auto"
    engine: str = "paddleocr"
    lang: str = "ch"


class OutputConfig(BaseModel):
    format: list[str] = Field(default_factory=lambda: ["mp3", "wav"])
    sample_rate: int = 24000
    segment_silence: float = 0.2
    chapter_silence: float = 1.0


class ServerConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8080


class AppConfig(BaseModel):
    llm: LLMConfig = Field(default_factory=LLMConfig)
    tts: TTSConfig = Field(default_factory=TTSConfig)
    ocr: OCRConfig = Field(default_factory=OCRConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    server: ServerConfig = Field(default_factory=ServerConfig)


def get_data_dir() -> Path:
    return Path(os.environ.get("PODFLOW_DATA_DIR", "data"))


def load_config() -> AppConfig:
    config_path = get_data_dir() / "config.yaml"
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}
        return AppConfig.model_validate(raw)
    return AppConfig()


def save_config(config: AppConfig) -> None:
    config_path = get_data_dir() / "config.yaml"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(config.model_dump(), f, allow_unicode=True, default_flow_style=False)

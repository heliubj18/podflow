from __future__ import annotations
from podflow.adapters.llm.base import BaseLLM
from podflow.adapters.llm.openai_compat import OpenAICompatLLM
from podflow.config import LLMConfig

PRESETS: dict[str, str] = {
    "ollama": "http://localhost:11434/v1",
    "llamacpp": "http://localhost:8002/v1",
    "openai": "https://api.openai.com/v1",
    "deepseek": "https://api.deepseek.com/v1",
    "siliconflow": "https://api.siliconflow.cn/v1",
}

def create_llm(config: LLMConfig) -> BaseLLM:
    base_url = config.base_url
    if not base_url and config.provider in PRESETS:
        base_url = PRESETS[config.provider]
    return OpenAICompatLLM(base_url=base_url, api_key=config.api_key, model=config.model)

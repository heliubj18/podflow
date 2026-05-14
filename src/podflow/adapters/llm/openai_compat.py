from __future__ import annotations
from openai import AsyncOpenAI
from podflow.adapters.llm.base import BaseLLM

class OpenAICompatLLM(BaseLLM):
    def __init__(self, base_url: str, api_key: str, model: str):
        self.model = model
        self.client = AsyncOpenAI(base_url=base_url, api_key=api_key or "sk-placeholder")

    async def chat(self, messages: list[dict[str, str]], temperature: float = 0.7, max_tokens: int = 4000) -> str:
        response = await self.client.chat.completions.create(
            model=self.model, messages=messages, temperature=temperature, max_tokens=max_tokens,
        )
        return response.choices[0].message.content or ""

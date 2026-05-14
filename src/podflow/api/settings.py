from fastapi import APIRouter
from pydantic import BaseModel

from podflow.config import AppConfig, load_config, save_config

router = APIRouter(tags=["settings"])


@router.get("/settings")
async def get_settings():
    config = load_config()
    return config.model_dump()


class SettingsUpdate(BaseModel):
    llm: dict | None = None
    tts: dict | None = None
    ocr: dict | None = None
    output: dict | None = None


@router.put("/settings")
async def update_settings(update: SettingsUpdate):
    config = load_config()
    if update.llm:
        config.llm = config.llm.model_copy(update=update.llm)
    if update.tts:
        config.tts = config.tts.model_copy(update=update.tts)
    if update.ocr:
        config.ocr = config.ocr.model_copy(update=update.ocr)
    if update.output:
        config.output = config.output.model_copy(update=update.output)
    save_config(config)
    return config.model_dump()


@router.post("/settings/test")
async def test_connection(backend: str = "llm"):
    config = load_config()
    if backend == "llm":
        from openai import AsyncOpenAI
        client = AsyncOpenAI(
            base_url=config.llm.base_url,
            api_key=config.llm.api_key or "sk-placeholder",
        )
        try:
            await client.models.list()
            return {"ok": True, "message": "LLM 连接成功"}
        except Exception as e:
            return {"ok": False, "message": f"LLM 连接失败: {e}"}
    return {"ok": False, "message": f"未知后端: {backend}"}

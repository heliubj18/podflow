from __future__ import annotations
import io
import edge_tts
from podflow.adapters.tts.base import BaseTTS

EDGE_VOICES = [
    {"id": "zh-CN-XiaoxiaoNeural", "name": "晓晓 (女声)"},
    {"id": "zh-CN-YunxiNeural", "name": "云希 (男声)"},
    {"id": "zh-CN-YunjianNeural", "name": "云健 (男声)"},
    {"id": "zh-CN-XiaoyiNeural", "name": "晓伊 (女声)"},
    {"id": "en-US-JennyNeural", "name": "Jenny (Female, EN)"},
    {"id": "en-US-GuyNeural", "name": "Guy (Male, EN)"},
]


class EdgeTTS(BaseTTS):
    async def synthesize(self, text: str, voice: str) -> bytes:
        communicate = edge_tts.Communicate(text, voice)
        buffer = io.BytesIO()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                buffer.write(chunk["data"])
        return buffer.getvalue()

    def list_voices(self) -> list[dict[str, str]]:
        return EDGE_VOICES

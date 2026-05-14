from podflow.adapters.tts.edge import EdgeTTS, EDGE_VOICES
from podflow.adapters.tts.registry import create_tts
from podflow.config import TTSConfig


def test_edge_tts_list_voices():
    tts = EdgeTTS()
    voices = tts.list_voices()
    assert len(voices) >= 2
    ids = [v["id"] for v in voices]
    assert "zh-CN-XiaoxiaoNeural" in ids
    assert "zh-CN-YunxiNeural" in ids


def test_create_tts_edge():
    config = TTSConfig(provider="edge-tts")
    tts = create_tts(config)
    assert isinstance(tts, EdgeTTS)


def test_create_tts_unknown():
    import pytest
    config = TTSConfig(provider="unknown")
    with pytest.raises(ValueError):
        create_tts(config)

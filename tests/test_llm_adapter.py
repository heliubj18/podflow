from podflow.adapters.llm.registry import create_llm, PRESETS
from podflow.adapters.llm.openai_compat import OpenAICompatLLM
from podflow.config import LLMConfig

def test_create_llm_ollama():
    config = LLMConfig(provider="ollama", model="qwen3:27b")
    llm = create_llm(config)
    assert isinstance(llm, OpenAICompatLLM)
    assert llm.model == "qwen3:27b"

def test_create_llm_custom():
    config = LLMConfig(provider="custom", base_url="http://myserver:9000/v1", api_key="my-key", model="my-model")
    llm = create_llm(config)
    assert isinstance(llm, OpenAICompatLLM)
    assert llm.model == "my-model"

def test_presets_contain_expected():
    assert "ollama" in PRESETS
    assert "openai" in PRESETS
    assert "deepseek" in PRESETS

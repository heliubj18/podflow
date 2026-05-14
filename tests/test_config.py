from pathlib import Path
from podflow.config import AppConfig, load_config, save_config, get_data_dir


def test_default_config():
    config = AppConfig()
    assert config.llm.provider == "ollama"
    assert config.tts.provider == "edge-tts"
    assert config.ocr.enabled == "auto"
    assert config.server.port == 8080


def test_load_config_no_file(tmp_path, monkeypatch):
    monkeypatch.setenv("PODFLOW_DATA_DIR", str(tmp_path))
    config = load_config()
    assert config.llm.provider == "ollama"


def test_save_and_load_config(tmp_path, monkeypatch):
    monkeypatch.setenv("PODFLOW_DATA_DIR", str(tmp_path))
    config = AppConfig()
    config.llm.provider = "openai"
    config.llm.api_key = "sk-test"
    save_config(config)

    loaded = load_config()
    assert loaded.llm.provider == "openai"
    assert loaded.llm.api_key == "sk-test"
    assert (tmp_path / "config.yaml").exists()

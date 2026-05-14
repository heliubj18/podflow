import pytest
from fastapi.testclient import TestClient
from podflow.app import app


@pytest.fixture(autouse=True)
def setup_data_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("PODFLOW_DATA_DIR", str(tmp_path))


@pytest.fixture
def client():
    return TestClient(app)


def test_get_settings(client):
    response = client.get("/api/settings")
    assert response.status_code == 200
    data = response.json()
    assert data["llm"]["provider"] == "ollama"
    assert data["tts"]["provider"] == "edge-tts"


def test_update_settings(client):
    response = client.put("/api/settings", json={
        "llm": {"provider": "openai", "api_key": "sk-test123"},
    })
    assert response.status_code == 200
    assert response.json()["llm"]["provider"] == "openai"

    response = client.get("/api/settings")
    assert response.json()["llm"]["provider"] == "openai"

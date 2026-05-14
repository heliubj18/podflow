"""
Integration smoke test — verifies the full API flow without real LLM/TTS.
"""
import pytest
from fastapi.testclient import TestClient
from podflow.app import app
from podflow.task_manager import task_manager, TaskStatus


@pytest.fixture(autouse=True)
def setup(tmp_path, monkeypatch):
    monkeypatch.setenv("PODFLOW_DATA_DIR", str(tmp_path))


@pytest.fixture
def client():
    return TestClient(app)


def test_full_flow_with_file_upload(client):
    """Test: upload txt file -> task created -> can query status."""
    resp = client.post(
        "/api/tasks",
        files={"file": ("test.txt", b"This is a test document with enough content.", "text/plain")},
        data={"mode": "lecture", "template": "host_expert"},
    )
    assert resp.status_code == 200
    task_id = resp.json()["task_id"]

    resp = client.get(f"/api/tasks/{task_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["filename"] == "test.txt"
    assert data["mode"] == "lecture"
    assert len(data["stages"]) == 4


def test_settings_roundtrip(client):
    """Test: get defaults -> update -> verify persisted."""
    resp = client.get("/api/settings")
    assert resp.json()["llm"]["provider"] == "ollama"

    client.put("/api/settings", json={"llm": {"provider": "deepseek", "api_key": "sk-abc"}})
    resp = client.get("/api/settings")
    assert resp.json()["llm"]["provider"] == "deepseek"
    assert resp.json()["llm"]["api_key"] == "sk-abc"


def test_task_list_and_delete(client):
    resp = client.post(
        "/api/tasks",
        files={"file": ("a.txt", b"aaa", "text/plain")},
        data={"mode": "dialogue"},
    )
    task_id = resp.json()["task_id"]

    resp = client.get("/api/tasks")
    assert len(resp.json()) >= 1

    resp = client.delete(f"/api/tasks/{task_id}")
    assert resp.status_code == 200

    resp = client.get(f"/api/tasks/{task_id}")
    assert resp.status_code == 404

import pytest
from fastapi.testclient import TestClient
from podflow.app import app


@pytest.fixture(autouse=True)
def setup_data_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("PODFLOW_DATA_DIR", str(tmp_path))


@pytest.fixture
def client():
    return TestClient(app)


def test_create_task_with_file(client, tmp_path):
    response = client.post(
        "/api/tasks",
        files={"file": ("test.txt", b"hello world", "text/plain")},
        data={"mode": "lecture", "template": "host_expert"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    assert data["status"] == "pending"


def test_create_task_no_input(client):
    response = client.post("/api/tasks", data={"mode": "lecture"})
    assert response.status_code == 400


def test_list_tasks(client, tmp_path):
    client.post(
        "/api/tasks",
        files={"file": ("a.txt", b"aaa", "text/plain")},
        data={"mode": "lecture"},
    )
    response = client.get("/api/tasks")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_task(client, tmp_path):
    resp = client.post(
        "/api/tasks",
        files={"file": ("b.txt", b"bbb", "text/plain")},
        data={"mode": "dialogue"},
    )
    task_id = resp.json()["task_id"]
    response = client.get(f"/api/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["filename"] == "b.txt"


def test_delete_task(client, tmp_path):
    resp = client.post(
        "/api/tasks",
        files={"file": ("c.txt", b"ccc", "text/plain")},
        data={"mode": "lecture"},
    )
    task_id = resp.json()["task_id"]
    response = client.delete(f"/api/tasks/{task_id}")
    assert response.status_code == 200
    assert client.get(f"/api/tasks/{task_id}").status_code == 404


def test_get_nonexistent_task(client):
    assert client.get("/api/tasks/nonexistent").status_code == 404

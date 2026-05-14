from __future__ import annotations

import asyncio
import json
import uuid
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from podflow.config import get_data_dir


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StageStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class StageInfo(BaseModel):
    name: str
    status: StageStatus = StageStatus.PENDING
    progress: int = 0
    total: int = 0
    message: str = ""


class TaskMeta(BaseModel):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])
    filename: str = ""
    mode: str = "dialogue"
    template: str = "host_expert"
    status: TaskStatus = TaskStatus.PENDING
    stages: list[StageInfo] = Field(default_factory=lambda: [
        StageInfo(name="parse"),
        StageInfo(name="structure"),
        StageInfo(name="script"),
        StageInfo(name="tts"),
    ])
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    error: str = ""


class TaskManager:
    def __init__(self):
        self._ws_connections: dict[str, list[asyncio.Queue]] = {}

    def task_dir(self, task_id: str) -> Path:
        return get_data_dir() / "tasks" / task_id

    def create_task(self, filename: str, mode: str, template: str) -> TaskMeta:
        meta = TaskMeta(filename=filename, mode=mode, template=template)
        task_path = self.task_dir(meta.id)
        task_path.mkdir(parents=True, exist_ok=True)
        (task_path / "input").mkdir(exist_ok=True)
        self._save_meta(meta)
        return meta

    def get_task(self, task_id: str) -> TaskMeta | None:
        meta_path = self.task_dir(task_id) / "meta.json"
        if not meta_path.exists():
            return None
        return TaskMeta.model_validate_json(meta_path.read_text(encoding="utf-8"))

    def list_tasks(self) -> list[TaskMeta]:
        tasks_dir = get_data_dir() / "tasks"
        if not tasks_dir.exists():
            return []
        result = []
        for d in sorted(tasks_dir.iterdir(), reverse=True):
            meta_path = d / "meta.json"
            if meta_path.exists():
                result.append(TaskMeta.model_validate_json(meta_path.read_text(encoding="utf-8")))
        return result

    def delete_task(self, task_id: str) -> bool:
        import shutil
        task_path = self.task_dir(task_id)
        if task_path.exists():
            shutil.rmtree(task_path)
            return True
        return False

    def update_stage(self, task_id: str, stage_name: str, **kwargs: Any) -> None:
        meta = self.get_task(task_id)
        if not meta:
            return
        for stage in meta.stages:
            if stage.name == stage_name:
                for k, v in kwargs.items():
                    setattr(stage, k, v)
                break
        self._save_meta(meta)
        self._broadcast(task_id, {"stage": stage_name, **{k: v for k, v in kwargs.items()}})

    def set_task_status(self, task_id: str, status: TaskStatus, error: str = "") -> None:
        meta = self.get_task(task_id)
        if not meta:
            return
        meta.status = status
        meta.error = error
        self._save_meta(meta)
        self._broadcast(task_id, {"task_status": status.value, "error": error})

    def subscribe(self, task_id: str) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue()
        self._ws_connections.setdefault(task_id, []).append(queue)
        return queue

    def unsubscribe(self, task_id: str, queue: asyncio.Queue) -> None:
        conns = self._ws_connections.get(task_id, [])
        if queue in conns:
            conns.remove(queue)

    def _broadcast(self, task_id: str, data: dict) -> None:
        for queue in self._ws_connections.get(task_id, []):
            queue.put_nowait(data)

    def _save_meta(self, meta: TaskMeta) -> None:
        meta_path = self.task_dir(meta.id) / "meta.json"
        meta_path.write_text(meta.model_dump_json(indent=2), encoding="utf-8")


task_manager = TaskManager()

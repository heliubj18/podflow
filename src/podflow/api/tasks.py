import asyncio
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path

from podflow.task_manager import task_manager, TaskStatus
from podflow.pipeline.runner import run_pipeline

router = APIRouter(tags=["tasks"])


@router.post("/tasks")
async def create_task(
    file: UploadFile | None = File(None),
    url: str = Form(""),
    mode: str = Form("dialogue"),
    template: str = Form("host_expert"),
):
    if not file and not url:
        raise HTTPException(400, "Must provide either a file or a URL")

    filename = file.filename if file else url
    meta = task_manager.create_task(filename=filename, mode=mode, template=template)

    if file:
        input_path = task_manager.task_dir(meta.id) / "input" / file.filename
        with open(input_path, "wb") as f:
            content = await file.read()
            f.write(content)

    # Start pipeline in background
    asyncio.get_event_loop().create_task(run_pipeline(meta.id))
    return {"task_id": meta.id, "status": meta.status.value}


@router.get("/tasks")
async def list_tasks():
    tasks = task_manager.list_tasks()
    return [t.model_dump() for t in tasks]


@router.get("/tasks/{task_id}")
async def get_task(task_id: str):
    meta = task_manager.get_task(task_id)
    if not meta:
        raise HTTPException(404, "Task not found")
    return meta.model_dump()


@router.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    if not task_manager.delete_task(task_id):
        raise HTTPException(404, "Task not found")
    return {"ok": True}


@router.get("/tasks/{task_id}/download/{file_type}")
async def download_task_file(task_id: str, file_type: str):
    meta = task_manager.get_task(task_id)
    if not meta:
        raise HTTPException(404, "Task not found")

    tts_dir = task_manager.task_dir(task_id) / "stage4_tts"
    script_dir = task_manager.task_dir(task_id) / "stage3_script"

    file_map = {
        "mp3": tts_dir / "full_audio.mp3",
        "wav": tts_dir / "full_audio.wav",
        "txt": script_dir / "script_preview.txt",
    }

    path = file_map.get(file_type)
    if not path or not path.exists():
        raise HTTPException(404, f"File type '{file_type}' not available")

    return FileResponse(path, filename=f"{meta.filename}.{file_type}")

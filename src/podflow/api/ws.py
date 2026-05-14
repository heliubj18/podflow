import asyncio
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from podflow.task_manager import task_manager

router = APIRouter()


@router.websocket("/ws/{task_id}")
async def task_ws(websocket: WebSocket, task_id: str):
    await websocket.accept()
    queue = task_manager.subscribe(task_id)
    try:
        while True:
            data = await queue.get()
            await websocket.send_json(data)
    except WebSocketDisconnect:
        pass
    finally:
        task_manager.unsubscribe(task_id, queue)

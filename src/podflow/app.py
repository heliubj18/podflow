from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from podflow.api.tasks import router as tasks_router
from podflow.api.settings import router as settings_router
from podflow.api.ws import router as ws_router

app = FastAPI(title="PodFlow", version="0.1.0")

app.include_router(tasks_router, prefix="/api")
app.include_router(settings_router, prefix="/api")
app.include_router(ws_router)

# Serve static frontend files
web_dir = Path(__file__).parent / "web"
if web_dir.exists():
    app.mount("/", StaticFiles(directory=str(web_dir), html=True), name="static")

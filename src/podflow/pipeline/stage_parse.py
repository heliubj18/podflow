from __future__ import annotations
from pathlib import Path
from podflow.parsers.base import get_parser
from podflow.task_manager import TaskManager, StageStatus

async def run_parse(task_id: str, tm: TaskManager) -> str:
    tm.update_stage(task_id, "parse", status=StageStatus.RUNNING, message="开始解析文档...")
    task_dir = tm.task_dir(task_id)
    meta = tm.get_task(task_id)
    if not meta:
        raise RuntimeError(f"Task {task_id} not found")
    filename = meta.filename
    input_dir = task_dir / "input"
    output_dir = task_dir / "stage1_parse"
    output_dir.mkdir(exist_ok=True)
    if filename.startswith("http://") or filename.startswith("https://"):
        source = filename
    else:
        source = str(input_dir / filename)
    parser = get_parser(filename)
    text = await parser.parse(source)
    output_path = output_dir / "raw_text.txt"
    output_path.write_text(text, encoding="utf-8")
    char_count = len(text)
    tm.update_stage(task_id, "parse", status=StageStatus.COMPLETED, message=f"解析完成，共 {char_count} 字")
    return text

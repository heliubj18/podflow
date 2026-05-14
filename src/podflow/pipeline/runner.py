from __future__ import annotations
import traceback
from podflow.adapters.llm.registry import create_llm
from podflow.adapters.tts.registry import create_tts
from podflow.config import load_config
from podflow.pipeline.stage_parse import run_parse
from podflow.pipeline.stage_structure import run_structure
from podflow.pipeline.stage_script import run_script
from podflow.pipeline.stage_tts import run_tts
from podflow.task_manager import task_manager, TaskStatus

async def run_pipeline(task_id: str) -> None:
    try:
        task_manager.set_task_status(task_id, TaskStatus.RUNNING)
        config = load_config()
        meta = task_manager.get_task(task_id)
        if not meta:
            return
        llm = create_llm(config.llm)
        tts = create_tts(config.tts)
        raw_text = await run_parse(task_id, task_manager)
        chapters = await run_structure(task_id, task_manager, llm, raw_text)
        script = await run_script(task_id, task_manager, llm, chapters, mode=meta.mode, template_name=meta.template)
        host_voice = config.tts.host_voice
        guest_voice = config.tts.guest_voice
        if meta.mode == "lecture":
            host_voice = config.tts.voice
        await run_tts(task_id, task_manager, tts, script, host_voice=host_voice, guest_voice=guest_voice, output_config=config.output)
        task_manager.set_task_status(task_id, TaskStatus.COMPLETED)
    except Exception as e:
        task_manager.set_task_status(task_id, TaskStatus.FAILED, error=traceback.format_exc())

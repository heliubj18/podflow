from __future__ import annotations
import json
import re
from pathlib import Path
from podflow.adapters.llm.base import BaseLLM
from podflow.prompts.lecture import build_lecture_prompt
from podflow.prompts.dialogue import build_dialogue_prompt
from podflow.prompts import load_template
from podflow.task_manager import TaskManager, StageStatus

async def run_script(task_id: str, tm: TaskManager, llm: BaseLLM, chapters: list[dict], mode: str, template_name: str) -> dict:
    total = len(chapters)
    tm.update_stage(task_id, "script", status=StageStatus.RUNNING, total=total, message="开始生成剧本...")
    output_dir = tm.task_dir(task_id) / "stage3_script"
    output_dir.mkdir(exist_ok=True)
    template = load_template(template_name) if mode == "dialogue" else None
    script_chapters = []
    for i, chapter in enumerate(chapters):
        title = chapter["title"]
        content = chapter["content"]
        tm.update_stage(task_id, "script", progress=i, message=f"生成第 {i+1}/{total} 章: {title}")
        if mode == "dialogue" and template:
            result = await _generate_dialogue(llm, title, content, template)
        else:
            result = await _generate_lecture(llm, title, content)
        script_chapters.append({"title": title, "mode": mode, "content": result})
    script = {"chapters": script_chapters}
    (output_dir / "script.json").write_text(json.dumps(script, ensure_ascii=False, indent=2), encoding="utf-8")
    preview = _build_preview(script_chapters, mode)
    (output_dir / "script_preview.txt").write_text(preview, encoding="utf-8")
    tm.update_stage(task_id, "script", status=StageStatus.COMPLETED, progress=total, message=f"剧本生成完成，共 {total} 章")
    return script

async def _generate_lecture(llm: BaseLLM, title: str, content: str) -> str:
    prompt = build_lecture_prompt(title, content)
    return await llm.chat(messages=[{"role": "user", "content": prompt}], temperature=0.7, max_tokens=4000)

async def _generate_dialogue(llm: BaseLLM, title: str, content: str, template: dict) -> list[dict]:
    host = template["host"]
    guest = template["guest"]
    prompt = build_dialogue_prompt(title=title, content=content, host_name=host["name"], host_role=host["role"], host_style=host["style"], guest_name=guest["name"], guest_role=guest["role"], guest_style=guest["style"])
    response = await llm.chat(messages=[{"role": "user", "content": prompt}], temperature=0.7, max_tokens=4000)
    try:
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            data = json.loads(json_match.group())
            return data.get("dialogues", [])
    except (json.JSONDecodeError, KeyError):
        pass
    return [{"speaker": "host", "text": response}]

def _build_preview(chapters: list[dict], mode: str) -> str:
    lines = []
    for ch in chapters:
        lines.append(f"=== {ch['title']} ===\n")
        if mode == "dialogue" and isinstance(ch["content"], list):
            for d in ch["content"]:
                speaker = "🎤" if d["speaker"] == "host" else "👩‍⚕️"
                lines.append(f"{speaker} {d['text']}\n")
        else:
            lines.append(str(ch["content"]) + "\n")
        lines.append("")
    return "\n".join(lines)

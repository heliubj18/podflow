from __future__ import annotations
import json
import re
from pathlib import Path
from podflow.adapters.llm.base import BaseLLM
from podflow.prompts.structure import build_structure_prompt
from podflow.task_manager import TaskManager, StageStatus

DEFAULT_SEGMENT_SIZE = 4000

async def run_structure(task_id: str, tm: TaskManager, llm: BaseLLM, raw_text: str) -> list[dict]:
    tm.update_stage(task_id, "structure", status=StageStatus.RUNNING, message="分析章节结构...")
    output_dir = tm.task_dir(task_id) / "stage2_structure"
    output_dir.mkdir(exist_ok=True)
    chapters = await _detect_chapters_with_llm(llm, raw_text)
    if not chapters:
        chapters = _split_by_size(raw_text)
    result = {"chapters": chapters}
    (output_dir / "chapters.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    tm.update_stage(task_id, "structure", status=StageStatus.COMPLETED, message=f"结构化完成，共 {len(chapters)} 章节", total=len(chapters))
    return chapters

async def _detect_chapters_with_llm(llm: BaseLLM, text: str) -> list[dict]:
    prompt = build_structure_prompt(text)
    try:
        response = await llm.chat(messages=[{"role": "user", "content": prompt}], temperature=0.3, max_tokens=2000)
        json_match = re.search(r'\{[\s\S]*\}', response)
        if not json_match:
            return []
        data = json.loads(json_match.group())
        raw_chapters = data.get("chapters", [])
        if not raw_chapters:
            return []
        return _extract_chapters_by_markers(text, raw_chapters)
    except Exception:
        return []

def _extract_chapters_by_markers(text: str, raw_chapters: list[dict]) -> list[dict]:
    chapters = []
    for i, ch in enumerate(raw_chapters):
        title = ch.get("title", f"第{i+1}部分")
        start_marker = ch.get("start_marker", "")
        start_idx = text.find(start_marker) if start_marker else -1
        if start_idx == -1:
            continue
        if i + 1 < len(raw_chapters):
            next_marker = raw_chapters[i + 1].get("start_marker", "")
            end_idx = text.find(next_marker) if next_marker else len(text)
            if end_idx == -1:
                end_idx = len(text)
        else:
            end_idx = len(text)
        content = text[start_idx:end_idx].strip()
        if content:
            chapters.append({"title": title, "content": content})
    return chapters

def _split_by_size(text: str) -> list[dict]:
    chapters = []
    paragraphs = text.split("\n\n")
    current = ""
    chapter_idx = 1
    for para in paragraphs:
        if len(current) + len(para) > DEFAULT_SEGMENT_SIZE and current:
            chapters.append({"title": f"第{chapter_idx}部分", "content": current.strip()})
            chapter_idx += 1
            current = para
        else:
            current += "\n\n" + para if current else para
    if current.strip():
        chapters.append({"title": f"第{chapter_idx}部分", "content": current.strip()})
    return chapters

from __future__ import annotations
import io
from pathlib import Path
from typing import TYPE_CHECKING
from podflow.adapters.tts.base import BaseTTS
from podflow.config import OutputConfig
from podflow.task_manager import TaskManager, StageStatus

if TYPE_CHECKING:
    from pydub import AudioSegment

async def run_tts(task_id: str, tm: TaskManager, tts: BaseTTS, script: dict, host_voice: str, guest_voice: str, output_config: OutputConfig) -> Path:
    from pydub import AudioSegment

    chapters = script["chapters"]
    total = len(chapters)
    tm.update_stage(task_id, "tts", status=StageStatus.RUNNING, total=total, message="开始语音合成...")
    output_dir = tm.task_dir(task_id) / "stage4_tts"
    output_dir.mkdir(exist_ok=True)
    segment_silence = AudioSegment.silent(duration=int(output_config.segment_silence * 1000))
    chapter_silence = AudioSegment.silent(duration=int(output_config.chapter_silence * 1000))
    full_audio = AudioSegment.empty()
    for i, chapter in enumerate(chapters):
        tm.update_stage(task_id, "tts", progress=i, message=f"合成第 {i+1}/{total} 章: {chapter['title']}")
        chapter_audio = await _synthesize_chapter(tts, chapter, host_voice, guest_voice, segment_silence)
        chapter_path = output_dir / f"chapter_{i:02d}.wav"
        chapter_audio.export(str(chapter_path), format="wav")
        full_audio += chapter_audio + chapter_silence
    wav_path = output_dir / "full_audio.wav"
    full_audio.export(str(wav_path), format="wav")
    mp3_path = output_dir / "full_audio.mp3"
    full_audio.export(str(mp3_path), format="mp3", bitrate="128k")
    duration_secs = len(full_audio) / 1000
    mins = int(duration_secs // 60)
    secs = int(duration_secs % 60)
    tm.update_stage(task_id, "tts", status=StageStatus.COMPLETED, progress=total, message=f"合成完成，总时长 {mins}分{secs}秒")
    return mp3_path

async def _synthesize_chapter(tts: BaseTTS, chapter: dict, host_voice: str, guest_voice: str, segment_silence: "AudioSegment") -> "AudioSegment":
    from pydub import AudioSegment

    content = chapter["content"]
    mode = chapter.get("mode", "lecture")
    if mode == "dialogue" and isinstance(content, list):
        segments: list[AudioSegment] = []
        for dialogue in content:
            voice = host_voice if dialogue["speaker"] == "host" else guest_voice
            text = dialogue["text"]
            if not text.strip():
                continue
            audio_bytes = await tts.synthesize(text, voice)
            segment = AudioSegment.from_file(io.BytesIO(audio_bytes), format="mp3")
            segments.append(segment)
            segments.append(segment_silence)
        if segments:
            return sum(segments[1:], segments[0])
        return AudioSegment.empty()
    else:
        text = content if isinstance(content, str) else str(content)
        chunks = _split_text(text, 800)
        segments = []
        for chunk in chunks:
            audio_bytes = await tts.synthesize(chunk, host_voice)
            segment = AudioSegment.from_file(io.BytesIO(audio_bytes), format="mp3")
            segments.append(segment)
            segments.append(segment_silence)
        if segments:
            return sum(segments[1:], segments[0])
        return AudioSegment.empty()

def _split_text(text: str, max_chars: int) -> list[str]:
    sentences = text.replace("。", "。\n").replace("！", "！\n").replace("？", "？\n").split("\n")
    chunks: list[str] = []
    current = ""
    for sent in sentences:
        if len(current) + len(sent) > max_chars and current:
            chunks.append(current)
            current = sent
        else:
            current += sent
    if current.strip():
        chunks.append(current)
    return chunks

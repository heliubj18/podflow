import pytest
from podflow.task_manager import TaskManager, StageStatus
from podflow.pipeline.stage_parse import run_parse

@pytest.fixture
def tm(tmp_path, monkeypatch):
    monkeypatch.setenv("PODFLOW_DATA_DIR", str(tmp_path))
    return TaskManager()

@pytest.mark.asyncio
async def test_parse_txt_file(tm):
    meta = tm.create_task(filename="test.txt", mode="lecture", template="host_expert")
    input_dir = tm.task_dir(meta.id) / "input"
    (input_dir / "test.txt").write_text("Hello World 这是测试", encoding="utf-8")
    text = await run_parse(meta.id, tm)
    assert "Hello World" in text
    assert "这是测试" in text
    output = tm.task_dir(meta.id) / "stage1_parse" / "raw_text.txt"
    assert output.exists()
    updated_meta = tm.get_task(meta.id)
    parse_stage = [s for s in updated_meta.stages if s.name == "parse"][0]
    assert parse_stage.status == StageStatus.COMPLETED

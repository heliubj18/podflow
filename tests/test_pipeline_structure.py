import pytest
from podflow.pipeline.stage_structure import _split_by_size

def test_split_by_size_short_text():
    text = "短文本，不需要分段"
    chapters = _split_by_size(text)
    assert len(chapters) == 1
    assert chapters[0]["title"] == "第1部分"

def test_split_by_size_long_text():
    para1 = "这是第一段。" * 400
    para2 = "这是第二段。" * 400
    text = para1 + "\n\n" + para2
    chapters = _split_by_size(text)
    assert len(chapters) == 2
    assert chapters[0]["title"] == "第1部分"
    assert chapters[1]["title"] == "第2部分"

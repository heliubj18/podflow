from podflow.prompts.structure import build_structure_prompt
from podflow.prompts.lecture import build_lecture_prompt
from podflow.prompts.dialogue import build_dialogue_prompt
from podflow.prompts import load_template, list_templates

def test_build_structure_prompt():
    prompt = build_structure_prompt("这是一段测试文本")
    assert "测试文本" in prompt
    assert "JSON" in prompt

def test_build_lecture_prompt():
    prompt = build_lecture_prompt("第一章", "内容内容")
    assert "第一章" in prompt
    assert "口语化" in prompt

def test_build_dialogue_prompt():
    prompt = build_dialogue_prompt(title="测试章节", content="测试内容", host_name="晓东", host_role="主持人", host_style="活泼", guest_name="李老师", guest_role="专家", guest_style="专业")
    assert "晓东" in prompt
    assert "李老师" in prompt
    assert "JSON" in prompt

def test_load_template():
    tmpl = load_template("host_expert")
    assert tmpl["host"]["name"] == "晓东"
    assert tmpl["guest"]["name"] == "李老师"
    assert "voice" in tmpl["host"]

def test_list_templates():
    templates = list_templates()
    ids = [t["id"] for t in templates]
    assert "host_expert" in ids
    assert "two_friends" in ids
    assert "teacher_student" in ids

def test_load_template_not_found():
    import pytest
    with pytest.raises(FileNotFoundError):
        load_template("nonexistent")

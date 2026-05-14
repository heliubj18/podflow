STRUCTURE_PROMPT = """你是一个文本结构分析专家。请分析以下文本，识别其章节结构。

要求：
1. 识别文本中的章节/段落划分
2. 如果有明确的章节标题，按标题切分
3. 如果没有明确章节，按主题逻辑切分，每段 3000-5000 字
4. 输出严格的 JSON 格式

输出格式（严格 JSON，不要其他内容）：
{{
    "chapters": [
        {{"title": "章节标题", "start_marker": "章节开头的前20个字", "end_marker": "章节结尾的后20个字"}}
    ]
}}

以下是需要分析的文本：

{text}"""

def build_structure_prompt(text: str) -> str:
    preview = text[:6000]
    return STRUCTURE_PROMPT.format(text=preview)

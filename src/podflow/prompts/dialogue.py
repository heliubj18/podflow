DIALOGUE_PROMPT = """你是一个专业的播客编剧。请将以下内容改写成双人对话的播客形式。

角色设定：
- {host_name}（{host_role}）：{host_style}
- {guest_name}（{guest_role}）：{guest_style}

对话要求：
1. 开头有自然的播客开场问候
2. 对话要自然，像真实聊天
3. {host_name}负责提问、总结，{guest_name}负责解答
4. 每轮对话不要太长，3-5句话就切换
5. 加入自然的语气词：嗯、对、没错等
6. 结尾有本章小结

章节标题：{title}

章节内容：
{content}

请输出严格 JSON 格式（不要其他内容）：
{{
    "dialogues": [
        {{"speaker": "host", "text": "{host_name}说的话"}},
        {{"speaker": "guest", "text": "{guest_name}说的话"}}
    ]
}}"""

def build_dialogue_prompt(title: str, content: str, host_name: str, host_role: str, host_style: str, guest_name: str, guest_role: str, guest_style: str) -> str:
    return DIALOGUE_PROMPT.format(title=title, content=content, host_name=host_name, host_role=host_role, host_style=host_style, guest_name=guest_name, guest_role=guest_role, guest_style=guest_style)

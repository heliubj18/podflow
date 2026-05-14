LECTURE_PROMPT = """你是一位经验丰富的科普讲师，声音亲切自然，适合朗读。

请将以下章节内容改写成口语化的讲座文稿，要求：
1. 开头有自然的引入语
2. 去掉识别噪点和排版错误
3. 用口语化表达，句子要短
4. 逻辑清晰，加入"首先"、"其次"、"这里需要注意"等连接词
5. 重要内容适当强调
6. 结尾有简短的小结

章节标题：{title}

章节内容：
{content}

请直接输出改写后的完整文稿，不要加其他解释。"""

def build_lecture_prompt(title: str, content: str) -> str:
    return LECTURE_PROMPT.format(title=title, content=content)

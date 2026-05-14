from pathlib import Path
from podflow.parsers.base import BaseParser

class DocxParser(BaseParser):
    async def parse(self, source: str | Path) -> str:
        from docx import Document
        doc = Document(str(source))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n\n".join(paragraphs)

from __future__ import annotations
from abc import ABC, abstractmethod
from pathlib import Path

class BaseParser(ABC):
    @abstractmethod
    async def parse(self, source: str | Path) -> str:
        """Parse the source and return extracted text."""

def get_parser(filename: str) -> BaseParser:
    ext = Path(filename).suffix.lower()
    if ext == ".txt":
        from podflow.parsers.txt import TxtParser
        return TxtParser()
    elif ext == ".pdf":
        from podflow.parsers.pdf import PdfParser
        return PdfParser()
    elif ext in (".doc", ".docx"):
        from podflow.parsers.docx import DocxParser
        return DocxParser()
    elif ext == ".epub":
        from podflow.parsers.epub import EpubParser
        return EpubParser()
    elif filename.startswith("http://") or filename.startswith("https://"):
        from podflow.parsers.url import UrlParser
        return UrlParser()
    else:
        raise ValueError(f"Unsupported file type: {ext}")

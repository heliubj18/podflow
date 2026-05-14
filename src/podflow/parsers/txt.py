from pathlib import Path
from podflow.parsers.base import BaseParser

class TxtParser(BaseParser):
    async def parse(self, source: str | Path) -> str:
        path = Path(source)
        return path.read_text(encoding="utf-8")

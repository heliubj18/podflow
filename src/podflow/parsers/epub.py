from pathlib import Path
from podflow.parsers.base import BaseParser

class EpubParser(BaseParser):
    async def parse(self, source: str | Path) -> str:
        import ebooklib
        from ebooklib import epub
        from bs4 import BeautifulSoup
        book = epub.read_epub(str(source), options={"ignore_ncx": True})
        texts: list[str] = []
        for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
            soup = BeautifulSoup(item.get_content(), "html.parser")
            text = soup.get_text(separator="\n", strip=True)
            if text:
                texts.append(text)
        return "\n\n".join(texts)

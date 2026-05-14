from pathlib import Path
from podflow.parsers.base import BaseParser

class UrlParser(BaseParser):
    async def parse(self, source: str | Path) -> str:
        import httpx
        from bs4 import BeautifulSoup
        async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
            resp = await client.get(str(source))
            resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "header", "footer", "aside"]):
            tag.decompose()
        main = soup.find("article") or soup.find("main") or soup.find("body")
        if main is None:
            return soup.get_text(separator="\n", strip=True)
        return main.get_text(separator="\n", strip=True)

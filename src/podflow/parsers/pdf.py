from __future__ import annotations
from pathlib import Path
from podflow.parsers.base import BaseParser

MIN_CHARS_PER_PAGE = 20

class PdfParser(BaseParser):
    async def parse(self, source: str | Path) -> str:
        import fitz
        doc = fitz.open(str(source))
        pages_text: list[str] = []
        ocr_pages: list[int] = []
        for i, page in enumerate(doc):
            text = page.get_text().strip()
            if len(text) >= MIN_CHARS_PER_PAGE:
                pages_text.append(text)
            else:
                pages_text.append("")
                ocr_pages.append(i)
        if ocr_pages:
            pages_text = await self._ocr_pages(doc, pages_text, ocr_pages)
        doc.close()
        return "\n\n".join(t for t in pages_text if t)

    async def _ocr_pages(self, doc, pages_text: list[str], ocr_pages: list[int]) -> list[str]:
        try:
            from podflow.adapters.ocr.paddleocr import PaddleOCRAdapter
            ocr = PaddleOCRAdapter()
            for i in ocr_pages:
                page = doc[i]
                pix = page.get_pixmap(dpi=300)
                img_bytes = pix.tobytes("png")
                text = await ocr.recognize_bytes(img_bytes)
                pages_text[i] = text
        except ImportError:
            pass
        return pages_text

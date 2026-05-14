import pytest
from pathlib import Path
from podflow.parsers.base import get_parser
from podflow.parsers.txt import TxtParser
from podflow.parsers.docx import DocxParser

@pytest.mark.asyncio
async def test_txt_parser(tmp_path):
    f = tmp_path / "test.txt"
    f.write_text("Hello World\n\nSecond paragraph", encoding="utf-8")
    parser = TxtParser()
    result = await parser.parse(f)
    assert "Hello World" in result
    assert "Second paragraph" in result

@pytest.mark.asyncio
async def test_get_parser_txt():
    parser = get_parser("file.txt")
    assert isinstance(parser, TxtParser)

@pytest.mark.asyncio
async def test_get_parser_pdf():
    from podflow.parsers.pdf import PdfParser
    parser = get_parser("file.pdf")
    assert isinstance(parser, PdfParser)

@pytest.mark.asyncio
async def test_get_parser_docx():
    parser = get_parser("file.docx")
    assert isinstance(parser, DocxParser)

@pytest.mark.asyncio
async def test_get_parser_url():
    from podflow.parsers.url import UrlParser
    parser = get_parser("https://example.com/article")
    assert isinstance(parser, UrlParser)

def test_get_parser_unsupported():
    with pytest.raises(ValueError):
        get_parser("file.xyz")

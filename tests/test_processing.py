import pytest

from src.processing import analyze, extract_text


class UploadedText:
    def __init__(self, content: str):
        self.content = content.encode("utf-8")

    def getvalue(self) -> bytes:
        return self.content


def test_extract_text_reads_uploaded_text():
    assert extract_text(UploadedText("Messy document text")) == "Messy document text"


def test_analyze_not_implemented():
    with pytest.raises(NotImplementedError):
        analyze("")

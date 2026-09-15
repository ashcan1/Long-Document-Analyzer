import pytest

from src.processing import analyze, clean_text, extract_text


class UploadedText:
    """Small test double that behaves like Streamlit's uploaded file."""

    def __init__(self, content: str):
        self.content = content.encode("utf-8")

    def getvalue(self) -> bytes:
        return self.content


def test_extract_text_reads_uploaded_text():
    """Extraction should turn uploaded bytes back into readable text."""
    assert extract_text(UploadedText("Messy document text")) == "Messy document text"


def test_clean_text_removes_extra_whitespace_without_changing_words():
    """Cleaning should remove formatting noise and preserve paragraph spacing."""
    messy_text = "\n  First line  \r\n\r\n\r\n  Second line\t \n"

    assert clean_text(messy_text) == "First line\n\nSecond line"


def test_analyze_not_implemented():
    """Analysis remains intentionally unfinished at this stage."""
    with pytest.raises(NotImplementedError):
        analyze("")

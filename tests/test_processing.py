from unittest.mock import MagicMock, patch

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


def test_analyze_parses_openai_response_into_analysis_result():
    """analyze() should send temperature=0.2 and parse the JSON reply."""
    fake_response = MagicMock()
    fake_response.choices[0].message.content = (
        '{"summary": "A sufficiently long summary.", '
        '"key_points": ["point one"], "confidence": 0.9}'
    )
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = fake_response

    with patch("src.processing.OpenAI", return_value=mock_client):
        result = analyze("Some document text")

    assert result.summary == "A sufficiently long summary."
    assert result.key_points == ["point one"]
    assert result.confidence == 0.9
    call_kwargs = mock_client.chat.completions.create.call_args.kwargs
    assert call_kwargs["temperature"] == 0.2
    assert "top_p" not in call_kwargs


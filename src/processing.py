from pydantic import ValidationError
from src.models import AnalysisResult


def extract_text(file) -> str:
    return file.getvalue().decode("utf-8")


def clean_text(text: str) -> str:
    if text is None or not text.strip():
        return ""

    cleaned_lines = []
    previous_line_was_blank = True

    for line in text.splitlines():
        cleaned_line = line.strip()
        if not cleaned_line:
            if not previous_line_was_blank:
                cleaned_lines.append("")
            previous_line_was_blank = True
            continue
        cleaned_lines.append(cleaned_line)
        previous_line_was_blank = False

    return "\n".join(cleaned_lines).strip()


def analyze(text: str) -> AnalysisResult:
    # Mock response — will be replaced with a real OpenAI call in the next step
    mock_llm_response = {
        "summary": (
            "This document has been processed by the analyzer. "
            "A real summary will appear once the OpenAI integration is added."
        ),
        "key_points": [
            "The document was successfully uploaded and cleaned.",
            "Pydantic is validating the structure of this response.",
            "Replace this mock with a real API call in the next step.",
        ],
        "confidence": 0.75,
    }

    # model_validate() builds the object AND runs all validators
    return AnalysisResult.model_validate(mock_llm_response)


def result_to_dict(result: AnalysisResult) -> dict:
    return result.model_dump()


def result_to_json(result: AnalysisResult) -> str:
    return result.model_dump_json(indent=2)

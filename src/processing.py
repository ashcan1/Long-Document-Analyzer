"""Document processing logic kept separate from the Streamlit user interface.

LEARNING: Why separate processing from the UI?
===============================================
Streamlit reruns the entire page script on every user interaction.
If all your logic lived in the page file, it would be harder to test,
reuse, or reason about. Keeping processing here means:
  - You can test these functions with plain Python (no browser needed).
  - The UI pages stay thin — they just call functions and display results.
  - When you swap Streamlit for another framework later, nothing here changes.
"""

import json

from pydantic import ValidationError

from src.models import AnalysisResult


# -----------------------------------------------------------------------
# STEP 1 — Extract
# -----------------------------------------------------------------------

def extract_text(file) -> str:
    """Convert an uploaded text file from bytes into a Python string.

    Streamlit gives us the uploaded file object. Its ``getvalue`` method
    returns bytes, so ``decode`` converts those bytes into readable text.
    """
    return file.getvalue().decode("utf-8")


# -----------------------------------------------------------------------
# STEP 2 — Clean
# -----------------------------------------------------------------------

def clean_text(text: str) -> str:
    """Clean formatting while preserving the document's words.

    The function processes one line at a time so it can remove extra spaces
    and keep paragraph breaks. It allows one blank line between paragraphs,
    but removes blank lines at the beginning and end of the document.
    """
    if text is None or not text.strip():
        return ""

    cleaned_lines = []

    # This prevents several consecutive blank lines from being copied.
    previous_line_was_blank = True

    # splitlines handles common Windows, Linux, and macOS line endings.
    for line in text.splitlines():
        # strip removes spaces and tabs around the line, not inside words.
        cleaned_line = line.strip()
        if not cleaned_line:
            # Keep only the first blank line after real content.
            if not previous_line_was_blank:
                cleaned_lines.append("")
            previous_line_was_blank = True
            continue

        # Keep non-empty lines in their original order.
        cleaned_lines.append(cleaned_line)
        previous_line_was_blank = False

    # Join the cleaned lines and remove outer blank space.
    return "\n".join(cleaned_lines).strip()


# -----------------------------------------------------------------------
# STEP 3 — Analyze
# -----------------------------------------------------------------------

def analyze(text: str) -> AnalysisResult:
    """Run analysis on cleaned text and return a validated AnalysisResult.

    LEARNING: The shape of this function
    =====================================
    The return type annotation `-> AnalysisResult` is a promise:
    this function will ALWAYS return a valid AnalysisResult, or raise
    an exception. It will never return None, a plain dict, or garbage.
    That guarantee is only possible because Pydantic validates the data
    before the object is created.

    Right now we use a hardcoded mock response (no real API call yet).
    In the next learning step (BPE Tokenization) we will replace this
    with a real OpenAI call — but the return type stays exactly the same.
    The UI page doesn't need to change at all. That's the benefit of a
    well-defined model.
    """

    # ------------------------------------------------------------------
    # LEARNING: Mock response — why start here?
    # ------------------------------------------
    # Building with a mock first lets you:
    #   1. Test the full pipeline (upload → clean → analyze → display)
    #      without needing an API key or internet connection.
    #   2. Understand exactly what shape of data the real API must return,
    #      before you write the API call.
    #   3. See Pydantic validation in action with controlled data.
    #
    # The mock pretends to be a JSON response from an LLM. This is the
    # exact format we will ask the real LLM to return later.
    # ------------------------------------------------------------------

    mock_llm_response = {
        "summary": (
            "This document has been processed by the analyzer. "
            "A real summary will appear here once the OpenAI integration "
            "is added in the next learning step."
        ),
        "key_points": [
            "The document was successfully uploaded and cleaned.",
            "Pydantic is validating the structure of this response.",
            "Replace this mock with a real API call in the next step.",
        ],
        "confidence": 0.75,
    }

    # ------------------------------------------------------------------
    # LEARNING: model_validate() — the Pydantic v2 way to build from a dict
    # -----------------------------------------------------------------------
    # `AnalysisResult.model_validate(dict)` is the v2 replacement for
    # the old `AnalysisResult.parse_obj(dict)`.
    #
    # It does three things in one call:
    #   1. Checks that all required fields are present (summary, key_points).
    #   2. Checks that each value matches its declared type.
    #   3. Runs your custom @field_validators (e.g. min length, min items).
    #
    # If anything fails, it raises ValidationError — which we catch below.
    # ------------------------------------------------------------------

    result = AnalysisResult.model_validate(mock_llm_response)
    return result


def analyze_with_bad_data() -> None:
    """Intentionally pass bad data to show what a ValidationError looks like.

    LEARNING: Run this function to see Pydantic catch errors
    =========================================================
    Call this from a Python shell or uncomment the block at the bottom
    of this file and run `python src/processing.py`.

    This is the most important experiment: watch Pydantic tell you
    *exactly* what is wrong, with field names and your custom messages.
    """

    bad_responses = [
        # Missing summary entirely
        {"key_points": ["point one"], "confidence": 0.9},
        # Summary too short
        {"summary": "Too short", "key_points": ["point one"], "confidence": 0.9},
        # Empty key_points list
        {"summary": "A valid long enough summary.", "key_points": [], "confidence": 0.9},
        # Confidence out of range
        {"summary": "A valid long enough summary.", "key_points": ["ok"], "confidence": 1.5},
    ]

    for i, bad_data in enumerate(bad_responses, start=1):
        print(f"\n--- Bad data experiment #{i} ---")
        print(f"Input: {bad_data}")
        try:
            AnalysisResult.model_validate(bad_data)
        except ValidationError as error:
            # LEARNING: ValidationError.errors() returns a list of dicts,
            # one per problem found. Each dict has:
            #   'loc'  — which field failed (e.g. ('summary',))
            #   'msg'  — the human-readable error message
            #   'type' — a machine-readable error code
            print("ValidationError caught!")
            for problem in error.errors():
                print(f"  Field : {problem['loc']}")
                print(f"  Error : {problem['msg']}")


# -----------------------------------------------------------------------
# LEARNING: Serialisation — getting data back OUT of a Pydantic model
# -----------------------------------------------------------------------

def result_to_dict(result: AnalysisResult) -> dict:
    """Convert an AnalysisResult back to a plain Python dict.

    LEARNING: model_dump()
    ----------------------
    model_dump() is the v2 name for the old .dict() method.
    It returns a plain dict — useful when you need to pass data to
    something that doesn't know about Pydantic (e.g. st.json() in
    Streamlit, or json.dumps() for saving to a file).
    """
    return result.model_dump()


def result_to_json(result: AnalysisResult) -> str:
    """Serialise an AnalysisResult to a JSON string.

    LEARNING: model_dump_json()
    ---------------------------
    model_dump_json() skips the intermediate dict and gives you a
    JSON string directly. Pydantic handles the serialisation of every
    field type — including nested models, datetimes, and custom types
    that plain json.dumps() would fail on.
    """
    return result.model_dump_json(indent=2)


# -----------------------------------------------------------------------
# Uncomment to run experiments directly from the terminal:
# python src/processing.py
# -----------------------------------------------------------------------
# if __name__ == "__main__":
#     # Experiment A — valid data goes through cleanly
#     print("=== Valid data ===")
#     valid_result = analyze("Some document text here.")
#     print(valid_result)
#     print(result_to_json(valid_result))
#
#     # Experiment B — bad data gets caught by Pydantic
#     print("\n=== Bad data experiments ===")
#     analyze_with_bad_data()

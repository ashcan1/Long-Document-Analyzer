"""Data models for the Long-Document Analyzer.

LEARNING: What is Pydantic and why use it?
==========================================
Pydantic is a library that uses Python type hints to validate data.
When you create an object from a Pydantic model, it checks that every
field has the right type and meets any rules you define.

Compare the OLD way (plain dataclass) vs the NEW way (Pydantic):

    OLD - Python dataclass (no validation):
        @dataclass
        class AnalysisResult:
            summary: str
            key_points: list[str]

        # This would silently accept garbage data:
        result = AnalysisResult(summary="", key_points=[])
        # No error raised — but empty data is useless!

    NEW - Pydantic BaseModel (with validation):
        class AnalysisResult(BaseModel):
            summary: str
            key_points: list[str]

        # Pydantic raises ValidationError on bad data:
        result = AnalysisResult(summary="", key_points=[])
        # → ValidationError: summary must have at least 10 characters

LEARNING: Pydantic v2 vs v1
============================
In Pydantic v2 (released 2023), validators use the @field_validator
decorator instead of the old @validator. The syntax is slightly different
but the idea is the same: run a function that checks or transforms a value
before it gets stored on the model.

Key v2 changes you'll see below:
  - `from pydantic import BaseModel, field_validator`  (not `validator`)
  - `@field_validator('field_name')`                   (not `@validator`)
  - `@classmethod` is required above every validator
  - `model_validate()` replaces the old `parse_obj()`
"""

from pydantic import BaseModel, field_validator, ValidationError

# Re-export ValidationError so other modules can import it from here
# without needing to know it lives in pydantic.
__all__ = ["AnalysisResult", "ValidationError"]


class AnalysisResult(BaseModel):
    """Structured output returned by the analysis step.

    LEARNING: BaseModel
    -------------------
    Inheriting from BaseModel is what makes this a Pydantic model.
    Every attribute you declare becomes a *validated field*. Pydantic
    reads the type hint (str, list[str], int, etc.) and rejects values
    that don't match — before your code ever touches the data.

    Fields
    ------
    summary    : A paragraph summarising the document.
    key_points : A list of the most important points found.
    confidence : A 0.0–1.0 score of how confident the model is.
                 Defaults to 1.0 if not provided.
    """

    summary: str
    key_points: list[str]
    confidence: float = 1.0

    # ------------------------------------------------------------------
    # LEARNING: field_validator
    # --------------------------
    # A field_validator is a function that runs automatically when the
    # model is created. If the function raises ValueError, Pydantic
    # turns it into a ValidationError with a helpful message.
    #
    # The decorator @field_validator('summary') means:
    #   "Run this function on the 'summary' field before storing it."
    #
    # 'mode="after"' means the value has already been type-checked
    # (confirmed to be a str) before our function runs.
    # ------------------------------------------------------------------

    @field_validator("summary", mode="after")
    @classmethod
    def summary_must_not_be_empty(cls, value: str) -> str:
        """Reject blank or very short summaries.

        LEARNING: Why validate this?
        An LLM can return an empty string if it hits an error or the
        document is unreadable. Catching it here means the rest of the
        app never has to handle a blank summary — it simply won't exist
        as a valid AnalysisResult.
        """
        if len(value.strip()) < 10:
            raise ValueError(
                "summary must be at least 10 characters — "
                "got an empty or near-empty response from the model."
            )
        return value.strip()  # also normalise whitespace while we're here

    @field_validator("key_points", mode="after")
    @classmethod
    def key_points_must_have_at_least_one(cls, value: list[str]) -> list[str]:
        """Require at least one key point.

        LEARNING: List validation
        You can validate list contents just like scalar fields. Here we
        check the length of the list. You could also loop through the
        items and validate each string individually if needed.
        """
        if len(value) == 0:
            raise ValueError(
                "key_points must contain at least one item — "
                "the model returned an empty list."
            )
        # Strip whitespace from every point while we're here.
        return [point.strip() for point in value if point.strip()]

    @field_validator("confidence", mode="after")
    @classmethod
    def confidence_must_be_between_zero_and_one(cls, value: float) -> float:
        """Keep the confidence score in the valid 0.0–1.0 range.

        LEARNING: Range validation
        Pydantic confirms the type is float, but it won't automatically
        check the range. That's what this validator does. You'll see this
        pattern a lot: Pydantic handles type, you handle business rules.
        """
        if not (0.0 <= value <= 1.0):
            raise ValueError(
                f"confidence must be between 0.0 and 1.0, got {value}."
            )
        return value


# ----------------------------------------------------------------------
# LEARNING: if __name__ == "__main__"
# ------------------------------------
# Python sets the special variable __name__ to "__main__" only when you
# run this file directly (python src/models.py).
# When another file imports models.py, __name__ is set to "src.models"
# instead, so this block is skipped automatically.
# That means: safe to leave this here forever — it won't interfere with
# the rest of the app.
# ----------------------------------------------------------------------

if __name__ == "__main__":

    print("\n" + "="*50)
    print("EXPERIMENT 1 — empty summary (should FAIL)")
    print("="*50)
    try:
        result = AnalysisResult(summary="", key_points=["point one"], confidence=0.9)
    except ValidationError as e:
        for problem in e.errors():
            print(f"  Field : {problem['loc']}")
            print(f"  Error : {problem['msg']}")

    print("\n" + "="*50)
    print("EXPERIMENT 2 — no key points (should FAIL)")
    print("="*50)
    try:
        result = AnalysisResult(summary="This is a valid summary.", key_points=[], confidence=0.9)
    except ValidationError as e:
        for problem in e.errors():
            print(f"  Field : {problem['loc']}")
            print(f"  Error : {problem['msg']}")

    print("\n" + "="*50)
    print("EXPERIMENT 3 — confidence out of range (should FAIL)")
    print("="*50)
    try:
        result = AnalysisResult(summary="Valid summary here.", key_points=["ok"], confidence=1.5)
    except ValidationError as e:
        for problem in e.errors():
            print(f"  Field : {problem['loc']}")
            print(f"  Error : {problem['msg']}")

    print("\n" + "="*50)
    print("EXPERIMENT 4 — everything valid (should PASS)")
    print("="*50)
    result = AnalysisResult(
        summary="This document discusses quarterly financial results.",
        key_points=["Revenue increased by 12%", "Operating costs were reduced"],
        confidence=0.95,
    )
    print(result)
    print("\nAs a dict  :", result.model_dump())
    print("\nAs JSON    :", result.model_dump_json())

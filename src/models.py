from pydantic import BaseModel, field_validator, ValidationError

__all__ = ["AnalysisResult", "ValidationError"]


class AnalysisResult(BaseModel):
    summary: str
    key_points: list[str]
    confidence: float = 1.0

    # Validator: summary must be at least 10 characters
    @field_validator("summary", mode="after")
    @classmethod
    def summary_must_not_be_empty(cls, value: str) -> str:
        if len(value.strip()) < 10:
            raise ValueError("summary must be at least 10 characters.")
        return value.strip()

    # Validator: key_points must have at least one item
    @field_validator("key_points", mode="after")
    @classmethod
    def key_points_must_have_at_least_one(cls, value: list[str]) -> list[str]:
        if len(value) == 0:
            raise ValueError("key_points must contain at least one item.")
        return [point.strip() for point in value if point.strip()]

    # Validator: confidence must be between 0.0 and 1.0
    @field_validator("confidence", mode="after")
    @classmethod
    def confidence_must_be_between_zero_and_one(cls, value: float) -> float:
        if not (0.0 <= value <= 1.0):
            raise ValueError(f"confidence must be between 0.0 and 1.0, got {value}.")
        return value


if __name__ == "__main__":

    print("\n--- Experiment 1: empty summary (should FAIL) ---")
    try:
        AnalysisResult(summary="", key_points=["point one"], confidence=0.9)
    except ValidationError as e:
        for p in e.errors():
            print(f"  Field: {p['loc']}  |  Error: {p['msg']}")

    print("\n--- Experiment 2: no key points (should FAIL) ---")
    try:
        AnalysisResult(summary="This is a valid summary.", key_points=[], confidence=0.9)
    except ValidationError as e:
        for p in e.errors():
            print(f"  Field: {p['loc']}  |  Error: {p['msg']}")

    print("\n--- Experiment 3: confidence out of range (should FAIL) ---")
    try:
        AnalysisResult(summary="Valid summary here.", key_points=["ok"], confidence=1.5)
    except ValidationError as e:
        for p in e.errors():
            print(f"  Field: {p['loc']}  |  Error: {p['msg']}")

    print("\n--- Experiment 4: everything valid (should PASS) ---")
    result = AnalysisResult(
        summary="This document discusses quarterly financial results.",
        key_points=["Revenue increased by 12%", "Operating costs were reduced"],
        confidence=0.95,
    )
    print(result)
    print("\nAs a dict:", result.model_dump())
    print("As JSON: ", result.model_dump_json())

from dataclasses import dataclass


@dataclass
class AnalysisResult:
    summary: str
    key_points: list[str]

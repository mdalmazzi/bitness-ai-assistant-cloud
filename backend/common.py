from dataclasses import dataclass
from typing import Optional

@dataclass
class Source:
    title: str
    document: str
    snippet: str
    score: Optional[float] = None
    page: Optional[str] = None

@dataclass
class AnswerResult:
    answer: str
    sources: list[Source]
    debug: dict | None = None

from pydantic import BaseModel, Field
from typing import List, Optional


class DocumentStats(BaseModel):
    word_count: int
    sentence_count: int
    paragraph_count: int
    character_count: int
    reading_time_minutes: float


class KeywordItem(BaseModel):
    keyword: str
    score: float


class NamedEntity(BaseModel):
    text: str
    label: str


class AnalysisResult(BaseModel):
    filename: str
    file_type: str
    language: str
    stats: DocumentStats
    keywords: List[KeywordItem]
    summary: str
    sentiment: str
    sentiment_score: float
    entities: List[NamedEntity]
    full_text: Optional[str] = Field(default=None, description="First 2000 chars of extracted text")

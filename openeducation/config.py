from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class SourceConfig(BaseModel):
    id: str
    type: Literal["markdown", "text", "pdf", "json", "csv"]
    path: str
    tags: List[str] = []
    license: Optional[str] = None


class DeckConfig(BaseModel):
    id: str = "deck_main"
    name: str = "OpenEducation"
    description: str = ""
    parent_id: Optional[str] = None
    tags: List[str] = []


class LLMConfig(BaseModel):
    provider: Literal["openai", "none"] = "openai"
    model: str = "gpt-4.1"
    temperature: float = 0.2


class RAGConfig(BaseModel):
    embedder: Literal["hash", "openai"] = "hash"
    embedding_model: str = "text-embedding-3-small"
    dims: int = 512
    top_k: int = 5
    use_faiss: bool = False


class SafetyConfig(BaseModel):
    allow_medical_actions: bool = False
    language: str = "en"


class AppConfig(BaseModel):
    data_dir: str = "data"
    seed: int = 7
    sources: List[SourceConfig] = Field(default_factory=list)
    deck: DeckConfig = DeckConfig()
    llm: LLMConfig = LLMConfig()
    rag: RAGConfig = RAGConfig()
    safety: SafetyConfig = SafetyConfig()

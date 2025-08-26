from typing import Optional

from pydantic import BaseModel


class UploadResponse(BaseModel):
    job_id: str
    deck_path: Optional[str] = None
    deck_id: Optional[str] = None
    notes: int
    title: Optional[str] = None


class HealthResponse(BaseModel):
    status: str


class DeckMeta(BaseModel):
    deck_id: str
    title: str
    notes: int
    created_at: str


class DeckListResponse(BaseModel):
    decks: list[DeckMeta]

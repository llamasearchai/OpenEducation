import os
import uuid
from typing import Any, Dict, List, Optional

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

from . import config
from .embeddings import embedding_dimension

DEFAULT_COLLECTION = config.QDRANT_COLLECTION


def get_client() -> QdrantClient:
    # Remote takes precedence if URL is provided
    if config.QDRANT_URL:
        return QdrantClient(url=config.QDRANT_URL, api_key=config.QDRANT_API_KEY)
    os.makedirs(config.QDRANT_PATH, exist_ok=True)
    # Local embedded Qdrant (no external server needed)
    return QdrantClient(path=config.QDRANT_PATH)


def ensure_collection(collection: str = DEFAULT_COLLECTION, dim: Optional[int] = None) -> None:
    client = get_client()
    dim = dim or embedding_dimension()
    if collection not in [c.name for c in client.get_collections().collections]:
        client.create_collection(
            collection_name=collection,
            vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
        )


def upsert_vectors(
    vectors: List[List[float]],
    payloads: List[Dict[str, Any]],
    ids: Optional[List[str]] = None,
    collection: str = DEFAULT_COLLECTION,
) -> List[str]:
    assert len(vectors) == len(payloads)
    ensure_collection(collection, dim=len(vectors[0]) if vectors else embedding_dimension())
    client = get_client()
    if ids is None:
        ids = [str(uuid.uuid4()) for _ in vectors]
    points = [
        PointStruct(id=pid, vector=vec, payload=pl)
        for pid, vec, pl in zip(ids, vectors, payloads)
    ]
    client.upsert(collection_name=collection, points=points)
    return ids


def search_similar(
    query_vector: List[float],
    limit: int = 5,
    collection: str = DEFAULT_COLLECTION,
    filter: Any = None,
):
    client = get_client()
    return client.search(
        collection_name=collection,
        query_vector=query_vector,
        limit=limit,
        query_filter=filter,
    )


def deck_filter(deck_id: str) -> Filter:
    return Filter(must=[FieldCondition(key="deck_id", match=MatchValue(value=deck_id))])


def scroll_all_by_deck(deck_id: str, collection: str = DEFAULT_COLLECTION, limit: int = 512):
    client = get_client()
    flt = deck_filter(deck_id)
    points = []
    next_page = None
    while True:
        res = client.scroll(collection_name=collection, scroll_filter=flt, with_payload=True, with_vectors=False, limit=limit, offset=next_page)
        points.extend(res[0])
        next_page = res[1]
        if next_page is None:
            break
    return points

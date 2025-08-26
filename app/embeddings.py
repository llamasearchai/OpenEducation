from typing import List
from openai import OpenAI
from . import config


def get_openai_client() -> OpenAI:
    if not config.OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not set")
    return OpenAI(api_key=config.OPENAI_API_KEY)


def embed_texts(texts: List[str], model: str | None = None) -> List[List[float]]:
    """Embed a batch of texts using OpenAI embeddings API.

    Returns list of embedding vectors (same order).
    """
    if not texts:
        return []
    client = get_openai_client()
    model_name = model or config.EMBEDDING_MODEL
    resp = client.embeddings.create(model=model_name, input=texts)
    # resp.data is a list of objects with .embedding
    return [d.embedding for d in resp.data]


def embedding_dimension(model: str | None = None) -> int:
    name = model or config.EMBEDDING_MODEL
    # Known dims for OpenAI embedding models
    if name == "text-embedding-3-large":
        return 3072
    if name == "text-embedding-3-small":
        return 1536
    # Fallback; callers should override if custom models
    return 3072

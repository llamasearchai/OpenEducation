from __future__ import annotations

import hashlib
from typing import List

import numpy as np
from dotenv import load_dotenv

load_dotenv()

try:
    from openai import OpenAI
except Exception:
    OpenAI = type(None)  # type: ignore


class EmbeddingBackend:
    def embed(self, texts: List[str]) -> np.ndarray:
        raise NotImplementedError


class HashEmbedding(EmbeddingBackend):
    def __init__(self, dims: int = 512, seed: int = 7) -> None:
        self.dims, self.seed = dims, seed

    def _vec(self, text: str) -> np.ndarray:
        v = np.zeros(self.dims, dtype=np.float32)
        for tok in text.lower().split():
            h = int(hashlib.sha1((tok + str(self.seed)).encode()).hexdigest()[:8], 16)
            v[h % self.dims] += 1.0
        if np.linalg.norm(v) > 0:
            v /= np.linalg.norm(v)
        return v

    def embed(self, texts: List[str]) -> np.ndarray:
        return np.vstack([self._vec(t) for t in texts])


class OpenAIEmbedding(EmbeddingBackend):
    def __init__(self, model: str = "text-embedding-3-large") -> None:
        if OpenAI is None:
            raise RuntimeError("openai not installed")
        self.client, self.model = OpenAI(), model

    def embed(self, texts: List[str]) -> np.ndarray:
        out = self.client.embeddings.create(model=self.model, input=texts)
        arr = np.array([d.embedding for d in out.data], dtype=np.float32)
        return arr / (np.linalg.norm(arr, axis=1, keepdims=True) + 1e-9)

    def get_dim(self) -> int:
        # This is for text-embedding-3-large. 
        # For other models, this value might need to be changed.
        return 3072

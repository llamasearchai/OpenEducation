from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

import numpy as np


@dataclass
class Index:
    ids: List[str]
    vecs: np.ndarray


def build_index(ids: List[str], vecs: np.ndarray) -> Index:
    return Index(ids=ids, vecs=vecs)


def search(index: Index, query_vec: np.ndarray, k: int = 5) -> List[Tuple[str, float]]:
    mat = index.vecs
    q = query_vec / (np.linalg.norm(query_vec) + 1e-9)
    sims = (mat @ q) / (np.linalg.norm(mat, axis=1) + 1e-9)
    order = np.argsort(-sims)[:k]
    return [(index.ids[i], float(sims[i])) for i in order]

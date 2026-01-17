import random
import hashlib

EMBEDDING_DIM = 384  # must match pgvector column

def embed_text(text: str):
    """
    Deterministic mock embeddings.
    Same text → same vector.
    """
    seed = int(hashlib.sha256(text.encode("utf-8")).hexdigest(), 16)
    random.seed(seed)
    return [random.random() for _ in range(EMBEDDING_DIM)]

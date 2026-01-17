import random
import hashlib

EMBEDDING_DIM = 384  # matches your pgvector column

def embed_text(text: str):
    """
    Deterministic mock embedding.
    Same text -> same vector.
    Enables full RAG flow without external API dependency.
    """
    seed = int(hashlib.sha256(text.encode("utf-8")).hexdigest(), 16)
    random.seed(seed)
    return [random.random() for _ in range(EMBEDDING_DIM)]

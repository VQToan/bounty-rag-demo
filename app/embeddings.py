"""Embeddings: OpenAI if key present, else deterministic hash fallback for demo."""
import hashlib
import math

from app import config


def _hash_embed(texts: list[str], dim: int = 32) -> list[list[float]]:
    out = []
    for t in texts:
        vec = [0.0] * dim
        for i in range(0, len(t), 4):
            h = int(hashlib.md5(t[i : i + 4].encode()).hexdigest(), 16)
            vec[h % dim] += 1.0
        n = math.sqrt(sum(v * v for v in vec)) or 1.0
        out.append([v / n for v in vec])
    return out


def embed_texts(texts: list[str]) -> list[list[float]]:
    if config.OPENAI_API_KEY:
        from openai import OpenAI

        client = OpenAI(api_key=config.OPENAI_API_KEY)
        resp = client.embeddings.create(model=config.EMBED_MODEL, input=texts)
        return [d.embedding for d in resp.data]
    # NOTE: gateway (9router/openrouter) thường không có embedding credentials,
    # nên retrieval dùng hash local 32-dim; LLM chat vẫn qua gateway.
    return _hash_embed(texts)

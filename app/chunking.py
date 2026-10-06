"""Minimal chunking for RAG ingest - idempotent, overlap-aware."""


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    text = text or ""
    if len(text) <= chunk_size:
        return [text] if text else []
    chunks: list[str] = []
    start = 0
    step = max(1, chunk_size - overlap)
    while start < len(text):
        chunks.append(text[start : start + chunk_size])
        if start + chunk_size >= len(text):
            break
        start += step
    return chunks

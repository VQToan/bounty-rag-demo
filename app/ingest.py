"""Ingest folder of PDF/txt -> chunk -> embed -> upsert pgvector. Idempotent."""
import hashlib
import sys
from pathlib import Path

from app import config
from app.chunking import chunk_text
from app.db import get_conn, init_db
from app.embeddings import embed_texts


def load_docs(folder: str) -> list[tuple[str, str]]:
    out = []
    for p in sorted(Path(folder).glob("**/*")):
        if p.suffix.lower() == ".txt":
            out.append((str(p), p.read_text(errors="ignore")))
        elif p.suffix.lower() == ".pdf":
            try:
                from pypdf import PdfReader

                text = "\n".join(pg.extract_text() or "" for pg in PdfReader(str(p)).pages)
                out.append((str(p), text))
            except Exception as e:
                print(f"[ingest] skip {p}: {e}")
    return out


def main(folder: str = "docs_data"):
    init_db()
    docs = load_docs(folder)
    if not docs:
        print(f"[ingest] no .txt/.pdf in {folder}")
        return
    with get_conn() as conn, conn.cursor() as cur:
        for path, text in docs:
            chunks = chunk_text(text, config.CHUNK_SIZE, config.CHUNK_OVERLAP)
            vecs = embed_texts(chunks)
            for i, (ch, vec) in enumerate(zip(chunks, vecs)):
                doc_id = hashlib.md5(f"{path}#{i}".encode()).hexdigest()
                if len(vec) == 1536:
                    cur.execute(
                        "INSERT INTO documents (id, content, embedding) VALUES (%s,%s,%s) "
                        "ON CONFLICT (id) DO UPDATE SET content=EXCLUDED.content, "
                        "embedding=EXCLUDED.embedding",
                        (doc_id, ch, str(vec)),
                    )
                else:
                    cur.execute(
                        "INSERT INTO documents (id, content, embedding32) VALUES (%s,%s,%s) "
                        "ON CONFLICT (id) DO UPDATE SET content=EXCLUDED.content, "
                        "embedding32=EXCLUDED.embedding32",
                        (doc_id, ch, str(vec)),
                    )
    print(f"[ingest] done: {len(docs)} files from {folder}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "docs_data")

"""Postgres + pgvector store. Falls back to stub when DB unreachable."""
from app import config

DDL = """
CREATE EXTENSION IF NOT EXISTS vector;
CREATE TABLE IF NOT EXISTS documents (
  id TEXT PRIMARY KEY,
  content TEXT NOT NULL,
  embedding vector(1536),
  embedding32 vector(32)
);
"""


def get_conn():
    import psycopg

    return psycopg.connect(config.DATABASE_URL, autocommit=True)


def init_db():
    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute(DDL)
    except Exception as e:
        print(f"[db] skip init (no DB?): {e}")


def search(query_vec: list[float], top_k: int) -> list[dict]:
    """Cosine similarity. Uses embedding32 for local demo, embedding for OpenAI."""
    try:
        col = "embedding" if len(query_vec) == 1536 else "embedding32"
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT content, 1 - ({col} <=> %s::vector) AS score "
                f"FROM documents ORDER BY {col} <=> %s::vector LIMIT %s",
                (str(query_vec), str(query_vec), top_k),
            )
            return [{"content": r[0], "score": float(r[1])} for r in cur.fetchall()]
    except Exception:
        return []

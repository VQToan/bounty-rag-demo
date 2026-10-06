#!/bin/bash
# Demo 60s for Loom / client: no docker required, uses TestClient stub mode.
set -e
cd "$(dirname "$0")/.."
.venv/bin/python -m pytest tests/ -q
.venv/bin/python - <<'PY'
from fastapi.testclient import TestClient
from app.main import app
c = TestClient(app)
print("GET /health:", c.get("/health").json())
for q in ["What is pgvector?", "How does ingest work?"]:
    r = c.post("/chat", json={"question": q, "top_k": 2})
    body = r.json()
    print(f"\nQ: {q}\nA: {body['answer'][:200]}...\nsources: {len(body['sources'])}")
PY
echo ""
echo "Docker (khi có Docker): docker compose up --build"
echo "  docker compose exec api python -m app.ingest docs_data"

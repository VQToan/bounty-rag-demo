# RAG Demo — FastAPI + Postgres pgvector + LangChain

Matches Upwork spec: ingest folder -> `/chat` RAG endpoint -> docker-compose 1 lệnh.

## 15-phút run

```bash
cp .env.example .env   # optional: thêm OPENAI_API_KEY để dùng LLM thật
docker compose up --build
# terminal 2:
docker compose exec api python -m app.ingest docs_data
curl localhost:8000/health
curl -X POST localhost:8000/chat -H 'Content-Type: application/json' \
  -d '{"question":"What is pgvector?","top_k":3}'
```

Không có `OPENAI_API_KEY` vẫn chạy demo mode (hash embedding + echo best match).

## Local dev (không docker)

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m pytest tests/ -v
.venv/bin/python -m uvicorn app.main:app --reload
```

## API

* `GET /health` -> `{"status":"ok"}`
* `POST /chat` `{question, top_k}` -> `{answer, sources:[{content, score}]}`

## Files

* `app/main.py` — FastAPI
* `app/ingest.py` — load txt/pdf, chunk, embed, upsert idempotent
* `app/chunking.py`, `app/embeddings.py`, `app/db.py`, `app/llm.py`
* `docker-compose.yml` — `pgvector/pgvector:pg16` + api

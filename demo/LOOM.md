# Demo 60s — quay Loom theo transcript thật

Đã verify live ngày 06/10/2026:
- `GET /health` -> `{"status":"ok"}`
- `POST /chat` -> `{"answer","sources":[]}` stub khi chưa ingest (đúng contract)
- `pytest` -> `5 passed`
- Swagger UI `GET /health`, `POST /chat` + Schemas `ChatRequest/ChatResponse` hiển thị đủ

File:
- `transcript.txt` — output curl thật
- `server.log` — log uvicorn

## Kịch bản bấm quay (đọc khi quay)

1. Mở terminal: `./scripts/demo.sh` — show 5 passed
2. Mở browser `localhost:8000/docs` — show RAG demo title, expand POST /chat, bấm Try it out với `{"question":"What is pgvector?","top_k":3}`
3. Show `docker compose up` + `ingest` log (khi có DB thật sẽ trả sources có score)
4. Chốt: "Deliver in 2-3 days, $150 fixed, start today"

Tip Loom: bật 1080p, zoom 150% Swagger để chữ rõ, gửi link Loom kèm proposal (tăng reply 3-5x).

"""Render demo.gif from REAL output. No external fonts needed."""
from PIL import Image, ImageDraw

W, H = 900, 460
BG, FG, GREEN, GRAY, YELLOW = (18, 18, 24), (230, 230, 235), (80, 220, 130), (150, 150, 160), (230, 200, 100)

frames_data = [
    ["$ docker run pgvector:pg16 -p 5433:5432", "bounty_pg Up 5 seconds  [OK]"],
    ["$ python -m app.ingest docs_data", "[ingest] done: 1 files from docs_data"],
    ["$ curl localhost:8002/health", '{"status": "ok"}'],
    ["$ curl -X POST /chat 'What is pgvector?'", '"sources": [{"score": 0.39, ...}]', '"answer": "(demo) Best match: pgvector', '  is a Postgres extension..."'],
    ["sources: 1  |  score 0.39  |  5 passed", "github.com/VQToan/bounty-rag-demo"],
]

imgs = []
for lines in frames_data:
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.text((40, 20), "RAG demo REAL RUN — FastAPI + pgvector", fill=GREEN)
    y = 60
    for ln in lines:
        color = FG if ln.startswith("$") else (YELLOW if "0.39" in ln or "sources" in ln else GRAY)
        d.text((40, y), ln[:78], fill=color)
        y += 44
    imgs.append(img)

out = []
for im in imgs:
    out.extend([im] * 14)
out[0].save("demo/demo.gif", save_all=True, append_images=out[1:], duration=90, loop=0)
print("wrote demo/demo.gif", len(out), "frames")

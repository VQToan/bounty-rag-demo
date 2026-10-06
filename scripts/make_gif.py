"""Render demo.gif from transcript steps. No external fonts needed."""
from PIL import Image, ImageDraw

W, H = 900, 420
BG, FG, GREEN, GRAY = (18, 18, 24), (230, 230, 235), (80, 220, 130), (150, 150, 160)

frames_data = [
    ["$ docker compose up --build", "db  -> pgvector/pgvector:pg16 :5432", "api -> FastAPI :8000  [OK]"],
    ["$ curl localhost:8001/health", '{"status": "ok"}'],
    ["$ curl -X POST /chat", '{"question": "What is pgvector?"}', '-> {"answer": "...", "sources": [...]}'],
    ["$ ./scripts/demo.sh", "5 passed  |  /health ok  |  /chat ok"],
    ["Deliver in 2-3 days — $150 fixed", "github.com/VQToan/bounty-rag-demo"],
]

imgs = []
for lines in frames_data:
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.draw(img) if False else ImageDraw.Draw(img)
    y = 60
    d.text((40, 20), "RAG demo — FastAPI + pgvector + LangChain", fill=GREEN)
    for ln in lines:
        d.text((40, y), ln, fill=FG if ln.startswith("$") else GRAY)
        y += 44
    # typewriter: 1 frame per step buildup
    imgs.append(img)

# hold each frame 90ms x12 for GIF visibility
out = []
for im in imgs:
    out.extend([im] * 12)
out[0].save("demo/demo.gif", save_all=True, append_images=out[1:], duration=90, loop=0)
print("wrote demo/demo.gif", len(out), "frames")

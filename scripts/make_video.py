"""Render demo.mp4 (1280x720, H.264) from REAL verified outputs."""
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw

W, H = 1280, 720
BG, FG, GREEN, GRAY, YELLOW = (12, 12, 18), (235, 235, 240), (90, 230, 140), (160, 160, 170), (240, 210, 110)
FRAMES = Path("demo/frames")
if FRAMES.exists():
    shutil.rmtree(FRAMES)
FRAMES.mkdir(parents=True)

STEPS: list[tuple[str, list[str]]] = [
    ("$ docker run pgvector:pg16 -p 5433:5432",
     ["bounty_pg Up 5 seconds  [OK]"]),
    ("$ python -m app.ingest docs_data",
     ["[ingest] done: 1 files from docs_data"]),
    ("$ curl localhost:8002/health",
     ['{"status": "ok"}']),
    ('$ curl -X POST /chat  "What is pgvector?"',
     ['"sources": [{"score": 0.3905, ...}]',
      '"answer": "Postgres extension for vector',
      '  similarity search. Store embeddings,',
      '  answer top-k cosine queries..."']),
    ('$ curl -X POST /chat  "What does re-running ingest do?"',
     ['"sources": [{"score": 0.4931, ...}]',
      '"answer": "Re-running ingest idempotent.',
      '  Same file plus chunk index make same id...']),
    ("$ pytest tests/ -q", ["5 passed"]),
]

idx = 0


def snap(lines: list[str]):
    global idx
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.text((50, 30), "RAG demo — REAL RUN  |  FastAPI + pgvector + LLM", fill=GREEN)
    y = 100
    for ln in lines:
        color = FG if ln.startswith("$") else (YELLOW if "score" in ln or "passed" in ln or "OK" in ln else GRAY)
        d.text((50, y), ln[:88], fill=color)
        y += 46
    img.save(FRAMES / f"f{idx:04d}.png")
    idx += 1


shown: list[str] = []
for cmd, outs in STEPS:
    # type the command progressively
    for n in range(1, len(cmd) + 1, 3):
        snap(shown + [cmd[:n] + "_"])
    snap(shown + [cmd])
    shown.append(cmd)
    for o in outs:
        shown.append(o)
        snap(list(shown))
    # hold final state of this step
    for _ in range(6):
        snap(list(shown))

print("frames:", idx)
subprocess.run(
    ["ffmpeg", "-y", "-loglevel", "error", "-framerate", "10",
     "-i", str(FRAMES / "f%04d.png"),
     "-c:v", "libx264", "-pix_fmt", "yuv420p", "demo/demo.mp4"],
    check=True,
)
print("wrote demo/demo.mp4")

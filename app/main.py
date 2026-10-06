from fastapi import FastAPI

from app import config
from app.db import search
from app.embeddings import embed_texts
from app.llm import answer
from app.schemas import ChatRequest, ChatResponse

app = FastAPI(title="RAG demo - FastAPI + pgvector + LangChain")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    qvec = embed_texts([req.question])[0]
    ctx = search(qvec, req.top_k or config.TOP_K_DEFAULT)
    return ChatResponse(answer=answer(req.question, ctx), sources=ctx)

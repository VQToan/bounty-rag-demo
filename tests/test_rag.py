"""RED: contract for RAG demo - must fail until app/ exists."""
from app.chunking import chunk_text
from app.schemas import ChatRequest, ChatResponse


def test_chunk_text_splits_with_overlap():
    text = "a" * 1200
    chunks = chunk_text(text, chunk_size=500, overlap=50)
    assert len(chunks) >= 2
    assert all(len(c) <= 500 for c in chunks)


def test_chunk_text_idempotent_input():
    text = "hello world " * 100
    c1 = chunk_text(text)
    c2 = chunk_text(text)
    assert c1 == c2


def test_chat_schemas():
    req = ChatRequest(question="What is pgvector?", top_k=3)
    assert req.question
    assert req.top_k == 3
    resp = ChatResponse(answer="x", sources=[{"content": "y", "score": 0.9}])
    assert resp.answer == "x"
    assert resp.sources[0]["score"] == 0.9


def test_health_endpoint():
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_chat_endpoint_contract():
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)
    r = client.post("/chat", json={"question": "hello", "top_k": 2})
    # without DB/LLM keys, must still return structured JSON (stub mode)
    assert r.status_code == 200
    body = r.json()
    assert "answer" in body
    assert "sources" in body
    assert isinstance(body["sources"], list)

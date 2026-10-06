"""Answer with LangChain if key present, else stub echo for demo/tests."""
from app import config


def answer(question: str, contexts: list[dict]) -> str:
    if config.OPENAI_API_KEY and contexts:
        from langchain_openai import ChatOpenAI

        llm = ChatOpenAI(model=config.LLM_MODEL, api_key=config.OPENAI_API_KEY)
        ctx = "\n\n".join(c["content"][:800] for c in contexts)
        msg = f"Answer using only this context:\n{ctx}\n\nQuestion: {question}"
        return llm.invoke(msg).content
    if not contexts:
        return "No indexed documents yet. Run: python -m app.ingest docs_data"
    top = contexts[0]["content"][:600]
    return f"(demo mode, no OPENAI_API_KEY) Best match:\n{top}\n\nQ: {question}"

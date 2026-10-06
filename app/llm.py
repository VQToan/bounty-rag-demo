"""Answer with LangChain if key present, else stub echo for demo/tests."""
from app import config


def _llm_kwargs():
    if config.OPENROUTER_API_KEY:
        return {
            "model": config.LLM_MODEL,
            "api_key": config.OPENROUTER_API_KEY,
            "base_url": config.OPENROUTER_BASE_URL,
        }
    return {"model": config.LLM_MODEL, "api_key": config.OPENAI_API_KEY}


def answer(question: str, contexts: list[dict]) -> str:
    if (config.OPENROUTER_API_KEY or config.OPENAI_API_KEY) and contexts:
        from langchain_openai import ChatOpenAI

        llm = ChatOpenAI(**_llm_kwargs())
        ctx = "\n\n".join(c["content"][:800] for c in contexts)
        msg = f"Answer using only this context:\n{ctx}\n\nQuestion: {question}"
        return llm.invoke(msg).content
    if not contexts:
        return "No indexed documents yet. Run: python -m app.ingest docs_data"
    top = contexts[0]["content"][:600]
    return f"(demo mode, no OPENAI_API_KEY/OPENROUTER_API_KEY) Best match:\n{top}\n\nQ: {question}"

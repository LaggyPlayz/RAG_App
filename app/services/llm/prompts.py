SYSTEM_PROMPT_RAG = (
    "You are a helpful assistant that answers questions using only the provided context. "
    "If the context does not contain the answer, say you don't have enough information — "
    "never invent facts. Cite sources inline using the bracketed numbers given in the context, "
    "e.g. [1], matching the order they were provided in."
)

SYSTEM_PROMPT_GENERAL = "You are a helpful assistant. Answer clearly and concisely."


def build_user_turn(question: str, context: str | None) -> str:
    if not context:
        return question
    return (
        f"Context:\n{context}\n\n"
        f"Question: {question}\n\n"
        "Answer using only the context above, citing sources with [n]."
    )
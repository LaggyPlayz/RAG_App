"""Token counting helpers, shared by history windowing and context building.

Uses tiktoken when available for accurate counts against OpenAI models;
falls back to a crude character-based heuristic so the rest of the
pipeline still works if tiktoken isn't installed.
"""

try:
    import tiktoken

    _ENCODER = tiktoken.get_encoding("cl100k_base")
except Exception:  # pragma: no cover - exercised only when tiktoken is missing
    _ENCODER = None


def count_tokens(text: str) -> int:
    if not text:
        return 0
    if _ENCODER is not None:
        return len(_ENCODER.encode(text))
    return max(1, len(text) // 4)


def truncate_to_tokens(text: str, max_tokens: int) -> str:
    if max_tokens <= 0:
        return ""
    if _ENCODER is not None:
        tokens = _ENCODER.encode(text)
        if len(tokens) <= max_tokens:
            return text
        return _ENCODER.decode(tokens[:max_tokens])
    approx_chars = max_tokens * 4
    return text[:approx_chars]
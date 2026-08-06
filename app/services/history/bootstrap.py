import uuid


def bootstrap_conversation(conversation_id: str | None = None) -> str:
    """Return the given conversation id unchanged, or mint a new one."""
    return conversation_id or str(uuid.uuid4())
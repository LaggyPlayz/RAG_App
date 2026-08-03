from app.models.history import HistoryMessage
from app.utils.token_utils import count_tokens


def apply_window(messages: list[HistoryMessage], max_messages: int, max_tokens: int) -> list[HistoryMessage]:
    """Keep the most recent messages within a message-count AND token budget.

    Always keeps at least the single most recent message if the budget
    is otherwise too tight for even one message.
    """
    recent = messages[-max_messages:] if max_messages > 0 else messages[:]

    windowed: list[HistoryMessage] = []
    used_tokens = 0
    for message in reversed(recent):
        tokens = count_tokens(message.content)
        if used_tokens + tokens > max_tokens and windowed:
            break
        windowed.append(message)
        used_tokens += tokens

    return list(reversed(windowed))
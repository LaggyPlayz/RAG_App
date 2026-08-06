from app.agents.state import AgentState
from app.core.constants import DATABASE, DOCUMENT, GENERAL, HYBRID
from app.services.llm.openai_service import OpenAIService


class IntentClassifierNode:
    def __init__(self, llm_service: OpenAIService):
        self.llm = llm_service

    async def classify(self, state: AgentState) -> AgentState:
        msg = state.get("user_message", "")
        has_db = bool(state.get("database_connection_ids"))
        has_doc = bool(state.get("knowledge_base_ids"))

        # Explicit fallback if sources not attached
        if not has_db and not has_doc:
            state["detected_intent"] = GENERAL
            return state
        elif has_db and not has_doc:
            state["detected_intent"] = DATABASE
            return state
        elif has_doc and not has_db:
            state["detected_intent"] = DOCUMENT
            return state

        # If both database and document sources are attached, classify intent with LLM
        prompt = [
            {
                "role": "system",
                "content": (
                    "Classify the user message into one of these exact intents:\n"
                    "- database: user is asking for database queries, stats, totals, counts, or tabular business records.\n"
                    "- document: user is asking about contract terms, policies, reports, text files, or file contents.\n"
                    "- hybrid: user is asking to compare or combine database data with uploaded document details.\n"
                    "- general: greeting, chitchat, or generic conversational input.\n"
                    "Output ONLY one word (database, document, hybrid, general)."
                ),
            },
            {"role": "user", "content": msg},
        ]

        intent = (await self.llm.complete(prompt)).strip().lower()
        if intent not in (DATABASE, DOCUMENT, HYBRID, GENERAL):
            intent = HYBRID

        state["detected_intent"] = intent
        return state

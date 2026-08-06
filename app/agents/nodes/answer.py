from app.agents.state import AgentState
from app.services.llm.openai_service import OpenAIService


class FinalAnswerGeneratorNode:
    def __init__(self, llm_service: OpenAIService):
        self.llm = llm_service

    async def generate(self, state: AgentState) -> AgentState:
        msg = state.get("user_message", "")
        context = state.get("merged_context") or state.get("document_context") or state.get("sql_markdown_result")

        if not context:
            prompt = [
                {"role": "system", "content": "You are a helpful AI assistant. Answer clearly and concisely."},
                {"role": "user", "content": msg},
            ]
        else:
            prompt = [
                {
                    "role": "system",
                    "content": (
                        "You are a helpful business intelligence AI assistant. "
                        "Answer the user's question using ONLY the provided evidence from database queries and/or uploaded documents.\n"
                        "Do NOT invent information or extrapolate beyond the provided data.\n"
                        "Cite document evidence using bracketed numbers [n] where applicable."
                    ),
                },
                {"role": "user", "content": f"Context Evidence:\n{context}\n\nUser Question: {msg}"},
            ]

        answer = await self.llm.complete(prompt)
        state["final_answer"] = answer
        return state

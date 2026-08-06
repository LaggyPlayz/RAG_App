from langgraph.graph import END, StateGraph

from app.agents.nodes.answer import FinalAnswerGeneratorNode
from app.agents.nodes.classifier import IntentClassifierNode
from app.agents.nodes.db_agent import DatabaseAgentNode
from app.agents.nodes.doc_agent import DocumentAgentNode
from app.agents.nodes.merger import HybridMergerNode
from app.agents.state import AgentState
from app.core.constants import DATABASE, DOCUMENT, GENERAL, HYBRID
from app.services.llm.openai_service import OpenAIService
from app.services.retrieval.context_builder import ContextBuilder
from app.services.retrieval.reranker import Reranker
from app.services.retrieval.retriever import Retriever
from app.services.sql.engine import SQLEngine


class ChatOrchestratorGraph:
    """LangGraph StateGraph orchestrating Multi-Tenant Chat (Database, Document RAG, Hybrid)."""

    def __init__(
        self,
        llm_service: OpenAIService,
        sql_engine: SQLEngine,
        retriever: Retriever,
        reranker: Reranker,
        context_builder: ContextBuilder,
    ):
        self.classifier_node = IntentClassifierNode(llm_service)
        self.db_node = DatabaseAgentNode(sql_engine)
        self.doc_node = DocumentAgentNode(retriever, reranker, context_builder)
        self.merger_node = HybridMergerNode()
        self.answer_node = FinalAnswerGeneratorNode(llm_service)

        self.workflow = self._build_workflow()

    def _route_intent(self, state: AgentState) -> str:
        intent = state.get("detected_intent", GENERAL)
        if intent == DATABASE:
            return "db_agent"
        elif intent == DOCUMENT:
            return "doc_agent"
        elif intent == HYBRID:
            return "hybrid_db"
        else:
            return "answer_gen"

    def _build_workflow(self):
        builder = StateGraph(AgentState)

        builder.add_node("classifier", self.classifier_node.classify)
        builder.add_node("db_agent", self.db_node.execute)
        builder.add_node("doc_agent", self.doc_node.retrieve)

        # Nodes for Hybrid workflow
        builder.add_node("hybrid_db", self.db_node.execute)
        builder.add_node("hybrid_doc", self.doc_node.retrieve)
        builder.add_node("merger", self.merger_node.merge)

        builder.add_node("answer_gen", self.answer_node.generate)

        builder.set_entry_point("classifier")

        builder.add_conditional_edges(
            "classifier",
            self._route_intent,
            {
                "db_agent": "db_agent",
                "doc_agent": "doc_agent",
                "hybrid_db": "hybrid_db",
                "answer_gen": "answer_gen",
            },
        )

        builder.add_edge("db_agent", "answer_gen")
        builder.add_edge("doc_agent", "answer_gen")

        # Hybrid chain
        builder.add_edge("hybrid_db", "hybrid_doc")
        builder.add_edge("hybrid_doc", "merger")
        builder.add_edge("merger", "answer_gen")

        builder.add_edge("answer_gen", END)

        return builder.compile()

    async def run(self, initial_state: AgentState) -> AgentState:
        return await self.workflow.ainvoke(initial_state)

import logging

from src.database.database import Database
from src.rag.llm import LLM
from src.database.embedding import Embedding

logger = logging.getLogger(__name__)


class RAG:
    def __init__(
        self, database: Database = None, llm: LLM = None, embedder: Embedding = None
    ):
        self.database = database
        self.llm = llm
        self.embedder = embedder
        if self.database is None or self.llm is None or self.embedder is None:
            raise ValueError(
                "All instances (Database, LLM, Embedding) must be provided to RAG."
            )

    def generate_prompt(self, question: str, n_results: int = 5):
        retrieved = self.database.parks.query(query_text=question, n_results=n_results)
        docs = retrieved.get("documents", [[]])[0]
        metas = retrieved.get("metadatas", [[]])[0]

        logger.info("Retrieved %d documents for question=%r", len(docs), question)

        if not docs:
            logger.warning(
                "CampLLM: I couldn't find relevant park info for that question."
            )
            return "I don't know based on the available park data."

        context_blocks = []
        for i, doc in enumerate(docs, start=1):
            meta = metas[i - 1] if i - 1 < len(metas) and metas[i - 1] else {}
            park_name = meta.get("parkName", "Unknown park")
            section_heading = meta.get("sectionHeading", "Unknown section")
            section_url = meta.get("sectionUrl", "N/A")
            logger.info(
                "Source %d park=%s section=%s url=%s snippet=%r",
                i,
                park_name,
                section_heading,
                section_url,
                doc[:160],
            )
            context_blocks.append(
                f"[Source {i}] park={park_name} | section={section_heading} | url={section_url}\n{doc}"
            )

        context = "\n\n".join(context_blocks)

        return f"""
Use ONLY the context below to answer.
If the answer is not in context, say: "I don't know based on the available park data."

Context:
{context}

User question:
{question}
"""

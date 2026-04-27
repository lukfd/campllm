import logging
import re

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

    def _build_context(self, question: str, n_results: int = 5):
        retrieved = self.database.parks.query(query_text=question, n_results=n_results)
        docs = retrieved.get("documents", [[]])[0]
        metas = retrieved.get("metadatas", [[]])[0]

        logger.info("Retrieved %d documents for question=%r", len(docs), question)

        if not docs:
            logger.warning(
                "CampLLM: I couldn't find relevant park info for that question."
            )
            return "", []

        context_blocks = []
        sources = []
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
            sources.append(
                {
                    "source_id": i,
                    "park_name": park_name,
                    "section_heading": section_heading,
                    "section_url": section_url,
                }
            )

        context = "\n\n".join(context_blocks)
        return context, sources

    def generate_prompt(self, question: str, n_results: int = 5):
        context, _ = self._build_context(question=question, n_results=n_results)

        return f"""
Use the retrieved park context below for park-specific facts.
Use your general knowledge only for broad geographic framing or plain-language explanation.
Use inline citations like [Source N] for any factual claim supported by retrieved context.
If you use only general knowledge, clearly say that it is general knowledge and not a retrieved park fact.

Retrieved park context:
{context if context else '[No retrieved park context available]'}

User question:
{question}
"""

    def ask(self, question: str, n_results: int = 5):
        context, sources = self._build_context(question=question, n_results=n_results)

        prompt = self.generate_prompt(question=question, n_results=n_results)
        answer = self.llm.send_message(prompt)
        cited_source_ids = sorted(
            {int(value) for value in re.findall(r"\[Source\s+(\d+)\]", answer)}
        )

        if cited_source_ids:
            filtered_sources = [
                source
                for source in sources
                if source["source_id"] in cited_source_ids
            ]
        else:
            filtered_sources = sources

        return {
            "answer": answer,
            "sources": filtered_sources,
            "cited_source_ids": cited_source_ids,
        }

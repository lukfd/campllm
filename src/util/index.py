import json
from pathlib import Path
import logging
from typing import Any

from src.database.collection.park import ParkCollection
from src.util.runner import Runner

logger = logging.getLogger(__name__)


class Indexer:
    def __init__(
        self,
        file: Path = Path("./parks_cleaned.jsonl"),
        park_collection: ParkCollection = None,
        chunk_size: int = 1000,
        max_workers: int | None = None,
    ):
        self.file = file
        if park_collection is None:
            raise ValueError("ParkCollection instance must be provided to Indexer.")
        self.park_collection = park_collection
        self.chunk_size = chunk_size
        self.runner = Runner(max_workers=max_workers)

    def index(self):
        logger.debug(f"Indexing file: {self.file}")
        with self.file.open("r", encoding="utf-8") as f:
            lines = [json.loads(line.strip()) for line in f if line.strip()]

        if not lines:
            logger.warning(f"No valid lines found in file: {self.file}")
            return

        logger.debug(
            f"Type of first line: {type(lines[0])} count: {len(lines)} keys: {list(lines[0].keys())}"
        )

        ids: list[str] = []
        documents_to_embed: list[str] = []
        metadata: list[dict[str, Any]] = []

        for line_ids, line_documents, line_metadata in self.runner.run_many(
            self._prepare_line_for_upsert, enumerate(lines)
        ):
            ids.extend(line_ids)
            documents_to_embed.extend(line_documents)
            metadata.extend(line_metadata)

        if not documents_to_embed:
            logger.warning(f"No chunks generated from file: {self.file}")
            return

        self._store_document(ids, documents_to_embed, metadata)

        logger.info(f"Upserted {len(ids)} chunks to Chroma.")

    def _chunk_clean_text(self, text: str, chunk_size: int = 1000):
        return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]

    def _prepare_line_for_upsert(
        self, indexed_line: tuple[int, dict[str, Any]]
    ) -> tuple[list[str], list[str], list[dict[str, Any]]]:
        line_idx, line = indexed_line
        logger.debug(f"Processing line with sectionUrl: {line.get('sectionUrl')}")

        if not line.get("cleanText"):
            raise ValueError(
                f"Missing cleanText in line with sectionUrl: {line.get('sectionUrl')}"
            )

        chunks = self._chunk_clean_text(line.get("cleanText", ""), self.chunk_size)
        if not chunks:
            return [], [], []

        base_id = line.get("sectionUrl") or f"unknown-{line_idx}"
        total_chunks = len(chunks)

        line_ids: list[str] = []
        line_documents: list[str] = []
        line_metadata: list[dict[str, Any]] = []

        for chunk_idx, chunk in enumerate(chunks):
            line_ids.append(f"{base_id}#chunk-{chunk_idx}")
            line_documents.append(chunk)
            line_metadata.append(
                {
                    "sectionUrl": line.get("sectionUrl"),
                    "parkName": line.get("parkName"),
                    "sectionId": line.get("sectionId"),
                    "sectionHeading": line.get("sectionHeading"),
                    "chunkIndex": chunk_idx,
                    "chunkCount": total_chunks,
                }
            )

        return line_ids, line_documents, line_metadata

    def _store_document(
        self,
        ids: list[str],
        documents_to_embed: list[str],
        metadata: list[dict[str, Any]],
    ):
        if not ids or not documents_to_embed:
            logger.debug(
                f"Empty ids or documents to embed. ids: {ids}, documents_to_embed count: {len(documents_to_embed)}"
            )
            raise ValueError("Missing values.")

        if len(ids) != len(documents_to_embed) or len(ids) != len(metadata):
            raise ValueError(
                "ids, documents_to_embed, and metadata must have matching lengths."
            )

        self.park_collection.upsert(
            ids=ids,
            documents=documents_to_embed,
            metadatas=metadata,
        )

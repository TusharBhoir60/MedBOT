"""
RAG Vector Store abstraction and ChromaDB implementation.
Provides a protocol interface so the backing store can be swapped
(ChromaDB → FAISS / Qdrant / Pinecone) without changing agent code.
"""
import functools
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Tuple

import chromadb
from chromadb.config import Settings as ChromaSettings

from ai_engine.state import MedicalDocument
from core.config import settings

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Protocol — swap implementations without touching agents
# ---------------------------------------------------------------------------

class VectorStoreProtocol(Protocol):
    """Abstract interface for any vector store backend."""

    def ingest_documents(self, documents: List[MedicalDocument]) -> int:
        """Ingest a batch of MedicalDocument objects. Returns count ingested."""
        ...

    def retrieve(self, query: str, top_k: int = 5) -> List[Tuple[MedicalDocument, float]]:
        """Return top-k documents with relevance scores (0-1, higher = more relevant)."""
        ...

    def is_available(self) -> bool:
        """Health-check: can the store be reached?"""
        ...

    def document_count(self) -> int:
        """Return the number of documents currently stored."""
        ...


# ---------------------------------------------------------------------------
# ChromaDB implementation
# ---------------------------------------------------------------------------

class ChromaVectorStore:
    """ChromaDB-backed vector store for the medical knowledge base."""

    COLLECTION_NAME = "medical_kb"

    def __init__(self, persist_dir: Optional[str] = None) -> None:
        self._persist_dir = persist_dir or settings.ai.chroma_persist_dir
        try:
            self._client = chromadb.PersistentClient(
                path=self._persist_dir,
                settings=ChromaSettings(anonymized_telemetry=False),
            )
            self._collection = self._client.get_or_create_collection(
                name=self.COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"},
            )
            logger.info(
                "ChromaDB initialised at %s  (docs: %d)",
                self._persist_dir,
                self._collection.count(),
            )
        except Exception as exc:
            logger.error("Failed to initialise ChromaDB: %s", exc)
            self._client = None  # type: ignore[assignment]
            self._collection = None  # type: ignore[assignment]

    # -- Protocol methods ---------------------------------------------------

    def ingest_documents(self, documents: List[MedicalDocument]) -> int:
        if not self._collection:
            logger.error("ChromaDB collection unavailable — cannot ingest.")
            return 0

        ids, docs, metas = [], [], []
        for doc in documents:
            ids.append(doc.id)
            docs.append(doc.content)
            metas.append({
                "title": doc.title,
                "source": doc.source,
                "category": doc.category,
                "version": doc.version or "",
            })

        self._collection.upsert(ids=ids, documents=docs, metadatas=metas)
        logger.info("Ingested %d documents into ChromaDB.", len(ids))
        return len(ids)

    @functools.lru_cache(maxsize=128)
    def retrieve(
        self, query: str, top_k: int = 5
    ) -> List[Tuple[MedicalDocument, float]]:
        if not self._collection:
            logger.error("ChromaDB collection unavailable — cannot retrieve.")
            return []

        if self._collection.count() == 0:
            logger.warning("Medical KB is empty — no documents to retrieve.")
            return []

        try:
            results = self._collection.query(
                query_texts=[query],
                n_results=min(top_k, self._collection.count()),
                include=["documents", "metadatas", "distances"],
            )
        except Exception as exc:
            logger.error("ChromaDB query failed: %s", exc)
            return []

        output: List[Tuple[MedicalDocument, float]] = []
        for idx in range(len(results["ids"][0])):
            meta = results["metadatas"][0][idx]
            doc = MedicalDocument(
                id=results["ids"][0][idx],
                title=meta.get("title", ""),
                source=meta.get("source", ""),
                category=meta.get("category", ""),
                content=results["documents"][0][idx],
                version=meta.get("version") or None,
            )
            # ChromaDB returns cosine *distance*; convert to similarity score
            distance = results["distances"][0][idx]
            similarity = max(0.0, 1.0 - (distance / 2.0))
            output.append((doc, similarity))

        # Sort by relevance descending
        output.sort(key=lambda x: x[1], reverse=True)
        return output

    def is_available(self) -> bool:
        return self._collection is not None

    def document_count(self) -> int:
        if not self._collection:
            return 0
        return self._collection.count()


# ---------------------------------------------------------------------------
# Helper — parse a structured markdown file into a MedicalDocument
# ---------------------------------------------------------------------------

def parse_medical_markdown(filepath: Path) -> MedicalDocument:
    """Parse a structured medical KB markdown file into a MedicalDocument."""
    text = filepath.read_text(encoding="utf-8")

    # Extract title from the first H1 heading
    title_match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else filepath.stem.replace("_", " ").title()

    # Extract source from a ## Source section if present
    source_match = re.search(r"^##\s+Source\s*\n(.+?)(?:\n#|$)", text, re.MULTILINE | re.DOTALL)
    source = source_match.group(1).strip() if source_match else "Medical Knowledge Base"

    # Derive category from filename
    category_map = {
        "dengue": "infectious",
        "malaria": "infectious",
        "hypertension": "chronic",
        "anemia": "chronic",
        "emergency_red_flags": "emergency",
    }
    category = category_map.get(filepath.stem, "general")

    return MedicalDocument(
        id=filepath.stem,
        title=title,
        source=source,
        category=category,
        content=text,
    )


# ---------------------------------------------------------------------------
# Singleton accessor
# ---------------------------------------------------------------------------

_store_instance: Optional[ChromaVectorStore] = None


def get_vector_store() -> ChromaVectorStore:
    """Return a singleton ChromaVectorStore instance."""
    global _store_instance
    if _store_instance is None:
        _store_instance = ChromaVectorStore()
    return _store_instance

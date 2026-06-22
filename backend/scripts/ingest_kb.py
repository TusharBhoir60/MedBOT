"""
Ingestion script for the Medical Knowledge Base.
Parses structured markdown files from backend/data/medical_kb/ and upserts
them into the ChromaDB vector store.

Usage:
    python -m scripts.ingest_kb
"""
import logging
import sys
from pathlib import Path

# Ensure the backend root is on PYTHONPATH so imports resolve
_backend_root = Path(__file__).resolve().parent.parent
if str(_backend_root) not in sys.path:
    sys.path.insert(0, str(_backend_root))

from ai_engine.rag.vector_store import (
    ChromaVectorStore,
    parse_medical_markdown,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(name)s | %(message)s")
logger = logging.getLogger(__name__)

KB_DIR = _backend_root / "data" / "medical_kb"


def ingest() -> int:
    """Parse all markdown files and ingest into ChromaDB. Returns count."""
    if not KB_DIR.exists():
        logger.error("Knowledge base directory not found: %s", KB_DIR)
        return 0

    md_files = sorted(KB_DIR.glob("*.md"))
    if not md_files:
        logger.warning("No markdown files found in %s", KB_DIR)
        return 0

    documents = []
    for md_path in md_files:
        try:
            doc = parse_medical_markdown(md_path)
            documents.append(doc)
            logger.info("Parsed: %s → %s", md_path.name, doc.title)
        except Exception as exc:
            logger.error("Failed to parse %s: %s", md_path.name, exc)

    store = ChromaVectorStore()
    count = store.ingest_documents(documents)
    logger.info("Ingestion complete — %d documents stored.", count)
    return count


if __name__ == "__main__":
    ingest()

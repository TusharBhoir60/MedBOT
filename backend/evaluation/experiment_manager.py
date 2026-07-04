"""
ExperimentManager: captures, serializes, and manages experiment metadata.
Records environment info, git state, and per-case retrieval diagnostics.
"""
import json
import os
import platform
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def _get_git_commit() -> Optional[str]:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None


def _get_git_branch() -> Optional[str]:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None


def _get_package_versions() -> Dict[str, str]:
    """Capture versions of key packages relevant to the evaluation."""
    packages = [
        "langchain", "langgraph", "openai", "chromadb",
        "pydantic", "fastapi", "numpy", "pytest"
    ]
    versions = {}
    import importlib.metadata
    for pkg in packages:
        try:
            versions[pkg] = importlib.metadata.version(pkg)
        except importlib.metadata.PackageNotFoundError:
            versions[pkg] = "not installed"
    return versions


class ExperimentManager:
    """
    Manages a single evaluation experiment: captures metadata, logs
    per-case retrieval diagnostics, and persists all artifacts.
    """

    def __init__(
        self,
        exp_dir: str,
        dataset_version: str = "v1",
        model_config: Optional[Dict[str, Any]] = None,
        seed: int = 42,
    ):
        self.exp_dir = exp_dir
        self.dataset_version = dataset_version
        self.seed = seed
        self.model_config = model_config or {}
        self.exp_id = os.path.basename(exp_dir)
        self.started_at = datetime.now(timezone.utc).isoformat()

        # Per-case retrieval diagnostics keyed by patient_id
        self._retrieval_log: Dict[str, List[Dict[str, Any]]] = {}

    def log_retrieval(
        self,
        adapter_name: str,
        patient_id: str,
        query: str,
        ranked_docs: List[str],
        similarity_scores: List[float],
        citations: List[str],
    ) -> None:
        """Record detailed retrieval diagnostics for a single case."""
        key = adapter_name
        if key not in self._retrieval_log:
            self._retrieval_log[key] = []
        self._retrieval_log[key].append({
            "patient_id": patient_id,
            "query": query,
            "ranked_docs": ranked_docs,
            "similarity_scores": similarity_scores,
            "citations": citations,
        })

    def build_metadata(self) -> Dict[str, Any]:
        """Assemble the complete experiment metadata snapshot."""
        return {
            "experiment_id": self.exp_id,
            "started_at": self.started_at,
            "dataset_version": self.dataset_version,
            "random_seed": self.seed,
            "git": {
                "commit": _get_git_commit(),
                "branch": _get_git_branch(),
            },
            "environment": {
                "python_version": sys.version,
                "platform": platform.platform(),
                "packages": _get_package_versions(),
            },
            "model_config": {
                "embedding_model": self.model_config.get("embedding_model", "unknown"),
                "llm_model": self.model_config.get("llm_model", "unknown"),
                "retrieval_top_k": self.model_config.get("retrieval_top_k", 5),
                "temperature": self.model_config.get("temperature", 0.0),
                "confidence_threshold": self.model_config.get("confidence_threshold", 0.7),
                "prompt_version": self.model_config.get("prompt_version", "v1"),
            },
        }

    def save(self) -> str:
        """Persist metadata.json and retrieval_diagnostics.json. Returns exp_dir."""
        metadata = self.build_metadata()
        with open(os.path.join(self.exp_dir, "metadata.json"), "w") as f:
            json.dump(metadata, f, indent=2)

        with open(os.path.join(self.exp_dir, "retrieval_diagnostics.json"), "w") as f:
            json.dump(self._retrieval_log, f, indent=2)

        return self.exp_dir

    @classmethod
    def load(cls, exp_dir: str) -> "ExperimentManager":
        """Load an ExperimentManager from a previously saved experiment directory."""
        metadata_path = os.path.join(exp_dir, "metadata.json")
        if not os.path.exists(metadata_path):
            raise FileNotFoundError(f"No metadata.json found in {exp_dir}")

        with open(metadata_path, "r") as f:
            meta = json.load(f)

        manager = cls(
            exp_dir=exp_dir,
            dataset_version=meta.get("dataset_version", "v1"),
            model_config=meta.get("model_config", {}),
            seed=meta.get("random_seed", 42),
        )
        manager.started_at = meta.get("started_at", manager.started_at)
        return manager

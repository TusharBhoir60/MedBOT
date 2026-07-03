"""
Replay utility: reproduce any previously saved evaluation experiment from
its persisted artifacts using the same configuration.
"""
import json
import os
import asyncio
from typing import Any, Dict, List, Optional

from backend.evaluation.datasets import load_dataset
from backend.evaluation.experiment_manager import ExperimentManager
from backend.evaluation.benchmark import (
    CMARWorkflowBaseline,
    LLMOnlyBaseline,
    RAGOnlyBaseline,
    RuleBasedBaseline,
)
from backend.evaluation.evaluator import Evaluator


def load_experiment_metadata(exp_dir: str) -> Dict[str, Any]:
    """Load the metadata.json from a saved experiment directory."""
    metadata_path = os.path.join(exp_dir, "metadata.json")
    if not os.path.exists(metadata_path):
        raise FileNotFoundError(f"No metadata.json found in {exp_dir}")
    with open(metadata_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_experiment_predictions(exp_dir: str) -> Dict[str, List[Dict[str, Any]]]:
    """Load the predictions.json from a saved experiment directory."""
    path = os.path.join(exp_dir, "predictions.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"No predictions.json found in {exp_dir}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


async def replay_experiment(exp_dir: str, output_dir: Optional[str] = None) -> str:
    """
    Reproduce an experiment from its saved metadata.
    Loads the original dataset version and model config, then runs the
    full evaluation pipeline again.

    Args:
        exp_dir:    Path to the original experiment directory.
        output_dir: Optional override for where to write the replay results.
                    If None, a new timestamped experiment directory is created.

    Returns:
        Path to the new experiment directory containing replay results.
    """
    meta = load_experiment_metadata(exp_dir)

    dataset_version = meta.get("dataset_version", "v1")
    seed = meta.get("random_seed", 42)
    model_config = meta.get("model_config", {})

    evaluator = Evaluator(
        data_path=dataset_version,
        seed=seed,
        dataset_version=dataset_version,
        model_config=model_config,
    )

    # Use mock adapters so replay works offline (no LLM keys required)
    adapters = [
        RuleBasedBaseline(),
        LLMOnlyBaseline(seed=seed),
        RAGOnlyBaseline(seed=seed),
        CMARWorkflowBaseline(seed=seed),
    ]

    new_exp_dir = await evaluator.run_evaluation(adapters=adapters)

    # Tag the replay directory with source info
    replay_meta_path = os.path.join(new_exp_dir, "replay_info.json")
    with open(replay_meta_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "replayed_from": exp_dir,
                "original_experiment_id": meta.get("experiment_id"),
                "original_started_at": meta.get("started_at"),
            },
            f,
            indent=2,
        )

    return new_exp_dir


def verify_replay_predictions(
    original_predictions: Dict[str, List[Dict[str, Any]]],
    replay_predictions: Dict[str, List[Dict[str, Any]]],
) -> Dict[str, Any]:
    """
    Compare predictions from original and replayed experiments.
    Returns a summary dict with match_rate per adapter and any mismatches.
    """
    report: Dict[str, Any] = {}

    for adapter_name in original_predictions:
        if adapter_name not in replay_predictions:
            report[adapter_name] = {"error": "adapter missing in replay"}
            continue

        orig = original_predictions[adapter_name]
        replay = replay_predictions[adapter_name]

        if len(orig) != len(replay):
            report[adapter_name] = {
                "error": f"case count mismatch: {len(orig)} vs {len(replay)}"
            }
            continue

        mismatches = []
        for o, r in zip(orig, replay):
            if o["predicted_diagnosis"] != r["predicted_diagnosis"]:
                mismatches.append({
                    "patient_id": o["patient_id"],
                    "original": o["predicted_diagnosis"],
                    "replay": r["predicted_diagnosis"],
                })

        total = len(orig)
        report[adapter_name] = {
            "total_cases": total,
            "matches": total - len(mismatches),
            "match_rate": (total - len(mismatches)) / total if total > 0 else 0.0,
            "mismatches": mismatches,
        }

    return report

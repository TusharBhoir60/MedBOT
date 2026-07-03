"""
Evaluator: orchestrates multi-adapter benchmark runs, computes all metrics,
and persists every artifact under backend/evaluation/results/<experiment_id>/.
"""
import json
import os
import random
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import numpy as np

from backend.evaluation.benchmark import (
    BenchmarkAdapter,
    CMARWorkflowBaseline,
    LLMOnlyBaseline,
    RAGOnlyBaseline,
    RuleBasedBaseline,
)
from backend.evaluation.calibration import CalibrationMetrics
from backend.evaluation.datasets import PatientCase, ReferralDecision, load_dataset
from backend.evaluation.experiment_manager import ExperimentManager
from backend.evaluation.metrics import MetricsCalculator
from backend.evaluation.report_generator import ReportGenerator


class Evaluator:
    def __init__(
        self,
        data_path: str = "latest",
        seed: int = 42,
        dataset_version: str = "v1",
        model_config: Optional[Dict[str, Any]] = None,
    ):
        self.data_path = data_path
        self.seed = seed
        self.dataset_version = dataset_version
        self.model_config = model_config or {}
        self._set_seed(seed)

        self.metrics_calc = MetricsCalculator()
        self.calib_calc = CalibrationMetrics()

    def _set_seed(self, seed: int) -> None:
        random.seed(seed)
        np.random.seed(seed)

    def _create_experiment_dir(self) -> str:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        exp_id = f"exp_{timestamp}_{uuid.uuid4().hex[:6]}"
        base_dir = os.path.dirname(os.path.abspath(__file__))
        exp_dir = os.path.join(base_dir, "results", exp_id)
        os.makedirs(exp_dir, exist_ok=True)
        return exp_dir

    async def run_evaluation(
        self,
        adapters: Optional[List[BenchmarkAdapter]] = None,
    ) -> str:
        cases = load_dataset(self.data_path)

        if adapters is None:
            adapters = [
                RuleBasedBaseline(),
                LLMOnlyBaseline(seed=self.seed),
                RAGOnlyBaseline(seed=self.seed),
                CMARWorkflowBaseline(seed=self.seed),
            ]

        exp_dir = self._create_experiment_dir()
        manager = ExperimentManager(
            exp_dir=exp_dir,
            dataset_version=self.dataset_version,
            model_config=self.model_config,
            seed=self.seed,
        )

        all_metrics: Dict[str, Any] = {}
        all_predictions: Dict[str, Any] = {}
        all_calibration: Dict[str, Any] = {}
        benchmark_summary: Dict[str, Any] = {}
        all_confusion: Dict[str, Any] = {}

        for adapter in adapters:
            name = adapter.get_name()

            ground_truths: List[str] = []
            predictions: List[str] = []
            confidences: List[float] = []
            binary_gts: List[int] = []
            gt_referrals: List[ReferralDecision] = []
            pred_referrals: List[ReferralDecision] = []
            retrieval_data: List[List[str]] = []
            case_records: List[Dict[str, Any]] = []

            for case in cases:
                result = await adapter.evaluate_case(case)

                gt_diag = case.ground_truth_diagnosis
                pred_diag = result.get("predicted_diagnosis", "Unknown")
                conf = float(result.get("confidence", 0.0))
                gt_ref = case.expected_referral_decision
                pred_ref = result.get("referral_decision", ReferralDecision.UNKNOWN)

                ground_truths.append(gt_diag)
                predictions.append(pred_diag)
                confidences.append(conf)
                binary_gts.append(1 if gt_diag == pred_diag else 0)
                gt_referrals.append(gt_ref)
                pred_referrals.append(pred_ref)
                retrieval_data.append(result.get("retrieved_docs", []))

                # Log detailed retrieval diagnostics
                manager.log_retrieval(
                    adapter_name=name,
                    patient_id=case.patient_id,
                    query=result.get("query", ""),
                    ranked_docs=result.get("retrieved_docs", []),
                    similarity_scores=result.get("similarity_scores", []),
                    citations=result.get("citations", []),
                )

                record = {
                    "patient_id": case.patient_id,
                    "ground_truth_diagnosis": gt_diag,
                    "predicted_diagnosis": pred_diag,
                    "ground_truth_referral": gt_ref.value,
                    "predicted_referral": pred_ref.value if isinstance(pred_ref, ReferralDecision) else pred_ref,
                    "confidence": conf,
                    "query": result.get("query", ""),
                    "retrieved_docs": result.get("retrieved_docs", []),
                    "similarity_scores": result.get("similarity_scores", []),
                    "citations": result.get("citations", []),
                }
                case_records.append(record)

            # ── Diagnostic metrics
            overall = self.metrics_calc.compute_overall_metrics(ground_truths, predictions)
            per_cond = self.metrics_calc.compute_per_condition_metrics(ground_truths, predictions)
            confusion = self.metrics_calc.compute_confusion_matrix(ground_truths, predictions)

            # ── Referral metrics
            referral_metrics = self.metrics_calc.compute_referral_metrics(gt_referrals, pred_referrals)

            # ── High-confidence error rate
            hcer = self.metrics_calc.compute_high_confidence_error_rate(
                ground_truths, predictions, confidences, threshold=0.8
            )

            # ── Retrieval metrics (mock relevant docs based on ground truth)
            mock_relevant = [{f"doc_{gt.replace(' ','_').lower()}_1",
                              f"doc_{gt.replace(' ','_').lower()}_2"}
                             for gt in ground_truths]
            retrieval_m = self.metrics_calc.compute_retrieval_metrics(mock_relevant, retrieval_data)

            # ── Calibration
            brier = self.calib_calc.compute_brier_score(binary_gts, confidences)
            ece, bin_stats = self.calib_calc.compute_ece_and_bins(binary_gts, confidences)
            opt_f1  = self.calib_calc.optimize_threshold(binary_gts, confidences, objective="f1")
            opt_sen = self.calib_calc.optimize_threshold(binary_gts, confidences, objective="sensitivity")
            opt_acc = self.calib_calc.optimize_threshold(binary_gts, confidences, objective="accuracy")

            adapter_metrics = {
                "overall": overall,
                "per_condition": per_cond,
                "referral": referral_metrics,
                "high_confidence_error_rate": hcer,
                "retrieval": retrieval_m,
                "calibration": {
                    "brier_score": brier,
                    "ece": ece,
                    "optimal_thresholds": {
                        "f1": opt_f1,
                        "sensitivity": opt_sen,
                        "accuracy": opt_acc,
                    },
                },
            }

            all_metrics[name] = adapter_metrics
            all_predictions[name] = case_records
            all_calibration[name] = bin_stats
            all_confusion[name] = confusion
            benchmark_summary[name] = {
                "accuracy": overall["accuracy"],
                "f1": overall["f1"],
                "ece": ece,
                "brier_score": brier,
                "referral_accuracy": referral_metrics["referral_accuracy"],
                "missed_emergency_rate": referral_metrics["missed_emergency_rate"],
                "high_confidence_error_rate": hcer,
            }

        # ── Persist artifacts
        def _dump(path: str, data: Any) -> None:
            with open(os.path.join(exp_dir, path), "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)

        _dump("metrics.json", all_metrics)
        _dump("predictions.json", all_predictions)
        _dump("calibration.json", all_calibration)
        _dump("benchmark_summary.json", benchmark_summary)
        _dump("confusion_matrix.json", all_confusion)

        manager.save()  # writes metadata.json and retrieval_diagnostics.json

        # ── Generate report
        report_gen = ReportGenerator(exp_dir=exp_dir)
        report_gen.generate_report()

        return exp_dir

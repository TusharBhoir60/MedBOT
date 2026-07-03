import os
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any
import random
import numpy as np
import asyncio

from backend.evaluation.datasets import PatientCase, load_dataset
from backend.evaluation.benchmark import BenchmarkAdapter, RuleBasedBaseline, LLMOnlyBaseline, RAGOnlyBaseline, CMARWorkflowBaseline
from backend.evaluation.metrics import MetricsCalculator
from backend.evaluation.calibration import CalibrationMetrics

class Evaluator:
    def __init__(self, data_path: str, seed: int = 42):
        self.data_path = data_path
        self.seed = seed
        self.set_seed(seed)
        
        self.metrics_calc = MetricsCalculator()
        self.calib_calc = CalibrationMetrics()
        
    def set_seed(self, seed: int):
        random.seed(seed)
        np.random.seed(seed)
        
    def create_experiment_dir(self) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        exp_id = f"exp_{timestamp}_{uuid.uuid4().hex[:6]}"
        
        # Determine base directory dynamically based on file location
        base_dir = os.path.dirname(os.path.abspath(__file__))
        exp_dir = os.path.join(base_dir, "results", exp_id)
        os.makedirs(exp_dir, exist_ok=True)
        return exp_dir
        
    async def run_evaluation(self, adapters: List[BenchmarkAdapter] = None) -> str:
        cases = load_dataset(self.data_path)
        
        if not adapters:
            adapters = [
                RuleBasedBaseline(),
                LLMOnlyBaseline(),
                RAGOnlyBaseline(),
                CMARWorkflowBaseline()
            ]
            
        exp_dir = self.create_experiment_dir()
        
        all_results = {}
        benchmark_summary = {}
        
        for adapter in adapters:
            adapter_name = adapter.get_name()
            
            ground_truths = []
            predictions = []
            confidences = []
            binary_gts = [] # For calibration (1 if correct, 0 if incorrect)
            retrieval_data = [] # List of retrieved docs
            
            case_results = []
            
            for case in cases:
                result = await adapter.evaluate_case(case)
                
                gt = case.ground_truth_diagnosis
                pred = result.get("predicted_diagnosis", "Unknown")
                conf = result.get("confidence", 0.0)
                
                ground_truths.append(gt)
                predictions.append(pred)
                confidences.append(conf)
                binary_gts.append(1 if gt == pred else 0)
                retrieval_data.append(result.get("retrieved_docs", []))
                
                case_results.append({
                    "patient_id": case.patient_id,
                    "ground_truth": gt,
                    "prediction": pred,
                    "confidence": conf,
                    "retrieved_docs": result.get("retrieved_docs", []),
                    "citation_scores": result.get("citation_scores", [])
                })
                
            # Compute Metrics
            overall_metrics = self.metrics_calc.compute_overall_metrics(ground_truths, predictions)
            per_condition_metrics = self.metrics_calc.compute_per_condition_metrics(ground_truths, predictions)
            confusion_matrix = self.metrics_calc.compute_confusion_matrix(ground_truths, predictions)
            
            # Mock relevant docs for retrieval metrics (ideally we'd have ground truth docs)
            mock_relevant_docs = [{f"doc_{gt}_1", f"doc_{gt}_2"} for gt in ground_truths]
            retrieval_metrics = self.metrics_calc.compute_retrieval_metrics(mock_relevant_docs, retrieval_data)
            
            # Calibration Metrics
            brier_score = self.calib_calc.compute_brier_score(binary_gts, confidences)
            ece, bin_stats = self.calib_calc.compute_ece_and_bins(binary_gts, confidences)
            opt_f1_threshold = self.calib_calc.optimize_threshold(binary_gts, confidences, objective='f1')
            opt_sens_threshold = self.calib_calc.optimize_threshold(binary_gts, confidences, objective='sensitivity')
            opt_acc_threshold = self.calib_calc.optimize_threshold(binary_gts, confidences, objective='accuracy')
            
            adapter_metrics = {
                "overall": overall_metrics,
                "per_condition": per_condition_metrics,
                "retrieval": retrieval_metrics,
                "calibration": {
                    "brier_score": brier_score,
                    "ece": ece,
                    "optimal_thresholds": {
                        "f1": opt_f1_threshold,
                        "sensitivity": opt_sens_threshold,
                        "accuracy": opt_acc_threshold
                    }
                }
            }
            
            all_results[adapter_name] = {
                "metrics": adapter_metrics,
                "predictions": case_results,
                "calibration_bins": bin_stats,
                "confusion_matrix": confusion_matrix
            }
            
            benchmark_summary[adapter_name] = {
                "accuracy": overall_metrics["accuracy"],
                "f1": overall_metrics["f1"],
                "ece": ece,
                "brier_score": brier_score
            }
            
        # Save outputs
        with open(os.path.join(exp_dir, "metrics.json"), "w") as f:
            json.dump({k: v["metrics"] for k, v in all_results.items()}, f, indent=2)
            
        with open(os.path.join(exp_dir, "predictions.json"), "w") as f:
            json.dump({k: v["predictions"] for k, v in all_results.items()}, f, indent=2)
            
        with open(os.path.join(exp_dir, "calibration.json"), "w") as f:
            json.dump({k: v["calibration_bins"] for k, v in all_results.items()}, f, indent=2)
            
        with open(os.path.join(exp_dir, "benchmark_summary.json"), "w") as f:
            json.dump(benchmark_summary, f, indent=2)
            
        with open(os.path.join(exp_dir, "confusion_matrix.json"), "w") as f:
            json.dump({k: v["confusion_matrix"] for k, v in all_results.items()}, f, indent=2)
            
        return exp_dir

import pytest
import os
import asyncio
from backend.evaluation.evaluator import Evaluator
from backend.evaluation.report_generator import ReportGenerator

@pytest.mark.asyncio
async def test_evaluator_end_to_end():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    json_path = os.path.join(base_dir, "data", "eval", "mock_dataset.json")
    
    if os.path.exists(json_path):
        evaluator = Evaluator(data_path=json_path)
        exp_dir = await evaluator.run_evaluation()
        
        assert os.path.exists(exp_dir)
        assert os.path.exists(os.path.join(exp_dir, "metrics.json"))
        assert os.path.exists(os.path.join(exp_dir, "predictions.json"))
        assert os.path.exists(os.path.join(exp_dir, "calibration.json"))
        assert os.path.exists(os.path.join(exp_dir, "benchmark_summary.json"))
        assert os.path.exists(os.path.join(exp_dir, "confusion_matrix.json"))
        
        report_gen = ReportGenerator(exp_dir=exp_dir)
        report_path = report_gen.generate_report()
        assert os.path.exists(report_path)

import pytest
from backend.evaluation.calibration import CalibrationMetrics
import math

def test_brier_score():
    calc = CalibrationMetrics()
    ground_truths = [1, 0, 1, 1]
    confidences = [0.9, 0.1, 0.8, 0.2]
    
    score = calc.compute_brier_score(ground_truths, confidences)
    # (0.1^2 + 0.1^2 + 0.2^2 + 0.8^2) / 4 = (0.01 + 0.01 + 0.04 + 0.64) / 4 = 0.70 / 4 = 0.175
    assert math.isclose(score, 0.175, rel_tol=1e-5)

def test_ece_and_bins():
    calc = CalibrationMetrics(num_bins=2)
    ground_truths = [1, 0, 1, 1]
    confidences = [0.9, 0.1, 0.8, 0.2]
    
    ece, bins = calc.compute_ece_and_bins(ground_truths, confidences)
    # Bins [0.0, 0.5], (0.5, 1.0]
    # Bin 1 (<=0.5): [0.1, 0.2] -> GT [0, 1]. Size=2, Acc=0.5, Conf=0.15. Weight=2/4=0.5. |Acc-Conf| = 0.35
    # Bin 2 (>0.5): [0.9, 0.8] -> GT [1, 1]. Size=2, Acc=1.0, Conf=0.85. Weight=2/4=0.5. |Acc-Conf| = 0.15
    # ECE = 0.5 * 0.35 + 0.5 * 0.15 = 0.175 + 0.075 = 0.25
    assert math.isclose(ece, 0.25, rel_tol=1e-5)
    assert len(bins) == 2

def test_optimize_threshold():
    calc = CalibrationMetrics()
    ground_truths = [1, 0, 1, 1]
    confidences = [0.9, 0.1, 0.8, 0.2]
    
    opt_f1 = calc.optimize_threshold(ground_truths, confidences, objective="f1")
    # Confidences: 0.1 (GT 0), 0.2 (GT 1). Best threshold is > 0.1 and <= 0.2.
    assert 0.1 < opt_f1 <= 0.21

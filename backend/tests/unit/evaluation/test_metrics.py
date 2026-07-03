"""Extended metrics tests covering referral metrics and high-confidence error rate."""
import pytest
import math

from backend.evaluation.metrics import MetricsCalculator
from backend.evaluation.datasets import ReferralDecision


calc = MetricsCalculator()


# ─── Existing diagnostic metric tests ─────────────────────────────────────

def test_overall_metrics():
    gt   = ["A", "B", "A", "C"]
    pred = ["A", "B", "C", "C"]
    m = calc.compute_overall_metrics(gt, pred)
    assert m["accuracy"] == 0.75
    assert math.isclose(m["precision"], 0.8333, rel_tol=1e-3)
    assert math.isclose(m["recall"],    0.8333, rel_tol=1e-3)


def test_per_condition_metrics():
    gt   = ["A", "B", "A", "C"]
    pred = ["A", "B", "C", "C"]
    m = calc.compute_per_condition_metrics(gt, pred)
    assert m["A"]["precision"] == 1.0
    assert m["A"]["recall"]    == 0.5
    assert m["B"]["precision"] == 1.0
    assert m["B"]["recall"]    == 1.0
    assert m["C"]["precision"] == 0.5
    assert m["C"]["recall"]    == 1.0


def test_confusion_matrix():
    gt   = ["A", "B", "A", "C"]
    pred = ["A", "B", "C", "C"]
    matrix = calc.compute_confusion_matrix(gt, pred)
    assert matrix["A"]["A"] == 1
    assert matrix["A"]["B"] == 0
    assert matrix["A"]["C"] == 1
    assert matrix["C"]["C"] == 1


def test_retrieval_metrics():
    relevant  = [{"doc1", "doc2"}, {"doc3"}]
    retrieved = [["doc2", "doc4", "doc5"], ["doc6", "doc3"]]
    m = calc.compute_retrieval_metrics(relevant, retrieved, k=2)
    assert m["recall_at_k"]    == 0.75
    assert m["precision_at_k"] == 0.5
    assert m["mrr"]            == 0.75
    assert m["ndcg"]           > 0.0


# ─── Referral metrics tests ────────────────────────────────────────────────

def _ref(val: str) -> ReferralDecision:
    return ReferralDecision(val)


def test_referral_metrics_perfect():
    gt   = [_ref("er"), _ref("immediate_clinic"), _ref("routine_checkup")]
    pred = [_ref("er"), _ref("immediate_clinic"), _ref("routine_checkup")]
    m = calc.compute_referral_metrics(gt, pred)
    assert m["referral_accuracy"]    == 1.0
    assert m["referral_precision"]   == 1.0
    assert m["referral_recall"]      == 1.0
    assert m["false_referral_rate"]  == 0.0
    assert m["missed_emergency_rate"] == 0.0


def test_referral_metrics_missed_emergency():
    # Two emergencies; one missed (returned routine_checkup instead of ER)
    gt   = [_ref("er"), _ref("er"), _ref("routine_checkup")]
    pred = [_ref("er"), _ref("routine_checkup"), _ref("routine_checkup")]
    m = calc.compute_referral_metrics(gt, pred)
    assert m["missed_emergency_rate"] == pytest.approx(0.5, rel=1e-4)


def test_referral_metrics_false_referral():
    # Non-referral case predicted as ER → FP
    gt   = [_ref("no_referral"), _ref("no_referral"), _ref("er")]
    pred = [_ref("er"),          _ref("no_referral"), _ref("er")]
    m = calc.compute_referral_metrics(gt, pred)
    # fp=1, tn=1 → false_referral_rate = 1/2 = 0.5
    assert m["false_referral_rate"] == pytest.approx(0.5, rel=1e-4)


def test_referral_metrics_empty():
    m = calc.compute_referral_metrics([], [])
    assert m["referral_accuracy"] == 0.0


# ─── High-confidence error rate tests ─────────────────────────────────────

def test_high_confidence_error_rate_zero():
    gt   = ["A", "A", "B"]
    pred = ["A", "A", "B"]
    conf = [0.9, 0.85, 0.95]
    rate = calc.compute_high_confidence_error_rate(gt, pred, conf, threshold=0.8)
    assert rate == 0.0


def test_high_confidence_error_rate_partial():
    # 1 high-conf error out of 2 high-conf predictions
    gt   = ["A", "B"]
    pred = ["A", "A"]   # B predicted as A with 0.9 conf
    conf = [0.9, 0.9]
    rate = calc.compute_high_confidence_error_rate(gt, pred, conf, threshold=0.8)
    assert rate == pytest.approx(0.5, rel=1e-4)


def test_high_confidence_error_rate_no_high_conf_predictions():
    gt   = ["A", "B"]
    pred = ["A", "X"]
    conf = [0.3, 0.4]
    rate = calc.compute_high_confidence_error_rate(gt, pred, conf, threshold=0.8)
    assert rate == 0.0

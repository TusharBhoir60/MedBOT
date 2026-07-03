import pytest
from backend.evaluation.metrics import MetricsCalculator
import math

def test_overall_metrics():
    calc = MetricsCalculator()
    ground_truths = ["A", "B", "A", "C"]
    predictions = ["A", "B", "C", "C"]
    
    metrics = calc.compute_overall_metrics(ground_truths, predictions)
    assert metrics["accuracy"] == 0.75
    # Macro avg logic:
    # A: TP=1, FP=0, FN=1 -> Prec=1.0, Rec=0.5 -> F1=0.666
    # B: TP=1, FP=0, FN=0 -> Prec=1.0, Rec=1.0 -> F1=1.0
    # C: TP=1, FP=1, FN=0 -> Prec=0.5, Rec=1.0 -> F1=0.666
    # Avg Prec = (1+1+0.5)/3 = 0.833
    # Avg Rec = (0.5+1+1)/3 = 0.833
    assert math.isclose(metrics["precision"], 0.8333, rel_tol=1e-3)
    assert math.isclose(metrics["recall"], 0.8333, rel_tol=1e-3)

def test_per_condition_metrics():
    calc = MetricsCalculator()
    ground_truths = ["A", "B", "A", "C"]
    predictions = ["A", "B", "C", "C"]
    
    metrics = calc.compute_per_condition_metrics(ground_truths, predictions)
    assert metrics["A"]["precision"] == 1.0
    assert metrics["A"]["recall"] == 0.5
    assert metrics["B"]["precision"] == 1.0
    assert metrics["B"]["recall"] == 1.0
    assert metrics["C"]["precision"] == 0.5
    assert metrics["C"]["recall"] == 1.0

def test_confusion_matrix():
    calc = MetricsCalculator()
    ground_truths = ["A", "B", "A", "C"]
    predictions = ["A", "B", "C", "C"]
    
    matrix = calc.compute_confusion_matrix(ground_truths, predictions)
    assert matrix["A"]["A"] == 1
    assert matrix["A"]["B"] == 0
    assert matrix["A"]["C"] == 1
    assert matrix["C"]["C"] == 1

def test_retrieval_metrics():
    calc = MetricsCalculator()
    relevant = [{"doc1", "doc2"}, {"doc3"}]
    retrieved = [["doc2", "doc4", "doc5"], ["doc6", "doc3"]]
    
    metrics = calc.compute_retrieval_metrics(relevant, retrieved, k=2)
    # Query 1: doc2 is at idx 0. hits=1. recall=1/2=0.5. precision=1/2=0.5. mrr=1/1=1.0. ndcg=1/log2(2)/ (1/log2(2) + 1/log2(3)) = 1 / 1.63 = 0.613
    # Query 2: doc3 is at idx 1. hits=1. recall=1/1=1.0. precision=1/2=0.5. mrr=1/2=0.5. ndcg=1/log2(3) / 1/log2(2) = 0.6309 / 1 = 0.6309
    
    assert metrics["recall_at_k"] == 0.75 # (0.5 + 1.0) / 2
    assert metrics["precision_at_k"] == 0.5 # (0.5 + 0.5) / 2
    assert metrics["mrr"] == 0.75 # (1.0 + 0.5) / 2
    assert metrics["ndcg"] > 0.0

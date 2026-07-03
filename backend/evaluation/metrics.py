from typing import List, Dict, Any, Set
from collections import defaultdict
import math

class MetricsCalculator:
    def __init__(self):
        pass

    def compute_overall_metrics(self, ground_truths: List[str], predictions: List[str]) -> Dict[str, float]:
        if not ground_truths:
            return {"accuracy": 0.0, "precision": 0.0, "recall": 0.0, "f1": 0.0}

        correct = sum(1 for gt, pred in zip(ground_truths, predictions) if gt == pred)
        accuracy = correct / len(ground_truths)

        # Macro average for Precision, Recall, F1
        conditions = set(ground_truths)
        metrics_per_condition = self.compute_per_condition_metrics(ground_truths, predictions)
        
        if not conditions:
            return {"accuracy": accuracy, "precision": 0.0, "recall": 0.0, "f1": 0.0}
            
        avg_precision = sum(m["precision"] for m in metrics_per_condition.values()) / len(conditions)
        avg_recall = sum(m["recall"] for m in metrics_per_condition.values()) / len(conditions)
        
        if avg_precision + avg_recall > 0:
            avg_f1 = 2 * (avg_precision * avg_recall) / (avg_precision + avg_recall)
        else:
            avg_f1 = 0.0

        return {
            "accuracy": accuracy,
            "precision": avg_precision,
            "recall": avg_recall,
            "f1": avg_f1
        }

    def compute_per_condition_metrics(self, ground_truths: List[str], predictions: List[str]) -> Dict[str, Dict[str, float]]:
        conditions = set(ground_truths)
        metrics = {}
        
        for condition in conditions:
            tp = sum(1 for gt, pred in zip(ground_truths, predictions) if gt == condition and pred == condition)
            fp = sum(1 for gt, pred in zip(ground_truths, predictions) if gt != condition and pred == condition)
            fn = sum(1 for gt, pred in zip(ground_truths, predictions) if gt == condition and pred != condition)
            
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
            
            metrics[condition] = {
                "precision": precision,
                "recall": recall,
                "f1": f1
            }
            
        return metrics

    def compute_confusion_matrix(self, ground_truths: List[str], predictions: List[str]) -> Dict[str, Dict[str, int]]:
        conditions = set(ground_truths).union(set(predictions))
        # Default all counts to 0
        matrix = {actual: {pred: 0 for pred in conditions} for actual in conditions}
        
        for gt, pred in zip(ground_truths, predictions):
            matrix[gt][pred] += 1
            
        return matrix

    def compute_retrieval_metrics(self, relevant_docs: List[Set[str]], retrieved_docs_lists: List[List[str]], k: int = 5) -> Dict[str, float]:
        """
        Computes retrieval metrics.
        relevant_docs: list of sets containing ground-truth relevant document IDs for each query.
        retrieved_docs_lists: list of lists containing retrieved document IDs for each query (ordered by relevance).
        """
        if not relevant_docs or not retrieved_docs_lists:
            return {"recall_at_k": 0.0, "precision_at_k": 0.0, "mrr": 0.0, "ndcg": 0.0}

        total_queries = len(relevant_docs)
        sum_recall = 0.0
        sum_precision = 0.0
        sum_mrr = 0.0
        sum_ndcg = 0.0
        
        for relevant, retrieved in zip(relevant_docs, retrieved_docs_lists):
            top_k = retrieved[:k]
            
            # Recall@K and Precision@K
            hits = len(set(top_k).intersection(relevant))
            sum_recall += hits / len(relevant) if relevant else 0.0
            sum_precision += hits / k if k > 0 else 0.0
            
            # MRR
            rr = 0.0
            for i, doc in enumerate(retrieved):
                if doc in relevant:
                    rr = 1.0 / (i + 1)
                    break
            sum_mrr += rr
            
            # nDCG
            dcg = 0.0
            for i, doc in enumerate(top_k):
                if doc in relevant:
                    dcg += 1.0 / math.log2(i + 2) # i=0 -> log2(2)=1
            
            idcg = 0.0
            for i in range(min(len(relevant), k)):
                idcg += 1.0 / math.log2(i + 2)
                
            sum_ndcg += dcg / idcg if idcg > 0 else 0.0

        return {
            "recall_at_k": sum_recall / total_queries,
            "precision_at_k": sum_precision / total_queries,
            "mrr": sum_mrr / total_queries,
            "ndcg": sum_ndcg / total_queries
        }

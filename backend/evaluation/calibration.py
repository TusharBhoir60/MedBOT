from typing import List, Dict, Any, Tuple
import numpy as np

class CalibrationMetrics:
    def __init__(self, num_bins: int = 10):
        self.num_bins = num_bins

    def compute_brier_score(self, ground_truths: List[int], confidences: List[float]) -> float:
        """
        Computes Brier Score.
        ground_truths: 1 if prediction is correct, 0 if incorrect.
        confidences: probability / confidence score between 0.0 and 1.0.
        """
        if not ground_truths:
            return 0.0
            
        gt_arr = np.array(ground_truths)
        conf_arr = np.array(confidences)
        return float(np.mean((conf_arr - gt_arr) ** 2))

    def compute_ece_and_bins(self, ground_truths: List[int], confidences: List[float]) -> Tuple[float, List[Dict[str, float]]]:
        """
        Computes Expected Calibration Error (ECE) and reliability bin statistics.
        """
        if not ground_truths:
            return 0.0, []

        gt_arr = np.array(ground_truths)
        conf_arr = np.array(confidences)
        
        bins = np.linspace(0.0, 1.0, self.num_bins + 1)
        bin_indices = np.digitize(conf_arr, bins, right=True)
        
        ece = 0.0
        n = len(ground_truths)
        bin_stats = []
        
        for i in range(1, self.num_bins + 1):
            mask = (bin_indices == i)
            # Edge case for 0.0 which falls into bin 0 when right=True
            if i == 1:
                mask = mask | (bin_indices == 0)
                
            bin_size = np.sum(mask)
            if bin_size > 0:
                bin_accuracy = np.mean(gt_arr[mask])
                bin_confidence = np.mean(conf_arr[mask])
                weight = bin_size / n
                ece += weight * np.abs(bin_accuracy - bin_confidence)
                
                bin_stats.append({
                    "bin_start": float(bins[i-1]),
                    "bin_end": float(bins[i]),
                    "count": int(bin_size),
                    "accuracy": float(bin_accuracy),
                    "confidence": float(bin_confidence)
                })
        
        return float(ece), bin_stats

    def optimize_threshold(self, ground_truths: List[int], confidences: List[float], objective: str = 'f1') -> float:
        """
        Finds the optimal confidence threshold based on a given objective.
        objective can be 'f1', 'accuracy', or 'sensitivity'
        """
        if not ground_truths:
            return 0.5
            
        thresholds = np.linspace(0.1, 0.9, 81) # 0.1 to 0.9 with 0.01 step
        best_threshold = 0.5
        best_score = -1.0
        
        gt_arr = np.array(ground_truths)
        conf_arr = np.array(confidences)
        
        for t in thresholds:
            preds = (conf_arr >= t).astype(int)
            
            tp = np.sum((preds == 1) & (gt_arr == 1))
            fp = np.sum((preds == 1) & (gt_arr == 0))
            fn = np.sum((preds == 0) & (gt_arr == 1))
            tn = np.sum((preds == 0) & (gt_arr == 0))
            
            if objective == 'f1':
                precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
                recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
                score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
            elif objective == 'accuracy':
                score = (tp + tn) / len(ground_truths)
            elif objective == 'sensitivity':
                score = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            else:
                score = (tp + tn) / len(ground_truths) # default to accuracy
                
            if score > best_score:
                best_score = score
                best_threshold = t
                
        return float(best_threshold)

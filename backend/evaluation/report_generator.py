import os
import json

class ReportGenerator:
    def __init__(self, exp_dir: str):
        self.exp_dir = exp_dir

    def generate_report(self):
        metrics_path = os.path.join(self.exp_dir, "metrics.json")
        summary_path = os.path.join(self.exp_dir, "benchmark_summary.json")
        
        if not os.path.exists(metrics_path) or not os.path.exists(summary_path):
            raise FileNotFoundError("Experiment data not found.")
            
        with open(metrics_path, "r") as f:
            metrics = json.load(f)
            
        with open(summary_path, "r") as f:
            summary = json.load(f)
            
        report_lines = []
        report_lines.append("# Clinical Validation & CMAR Calibration Report")
        report_lines.append(f"\n**Experiment ID:** {os.path.basename(self.exp_dir)}")
        
        report_lines.append("\n## Benchmark Summary")
        report_lines.append("| Model | Accuracy | F1 Score | ECE | Brier Score |")
        report_lines.append("|---|---|---|---|---|")
        
        for model, s in summary.items():
            report_lines.append(f"| {model} | {s['accuracy']:.4f} | {s['f1']:.4f} | {s['ece']:.4f} | {s['brier_score']:.4f} |")
            
        report_lines.append("\n## Detailed Metrics per Model")
        
        for model, m in metrics.items():
            report_lines.append(f"\n### {model}")
            
            report_lines.append("\n#### Overall Metrics")
            report_lines.append(f"- **Accuracy:** {m['overall']['accuracy']:.4f}")
            report_lines.append(f"- **Precision:** {m['overall']['precision']:.4f}")
            report_lines.append(f"- **Recall:** {m['overall']['recall']:.4f}")
            report_lines.append(f"- **F1 Score:** {m['overall']['f1']:.4f}")
            
            report_lines.append("\n#### Calibration")
            report_lines.append(f"- **Expected Calibration Error (ECE):** {m['calibration']['ece']:.4f}")
            report_lines.append(f"- **Brier Score:** {m['calibration']['brier_score']:.4f}")
            report_lines.append(f"- **Optimal Threshold (F1):** {m['calibration']['optimal_thresholds']['f1']:.2f}")
            report_lines.append(f"- **Optimal Threshold (Sensitivity):** {m['calibration']['optimal_thresholds']['sensitivity']:.2f}")
            report_lines.append(f"- **Optimal Threshold (Accuracy):** {m['calibration']['optimal_thresholds']['accuracy']:.2f}")
            
            report_lines.append("\n#### Retrieval Metrics")
            report_lines.append(f"- **Recall@K:** {m['retrieval']['recall_at_k']:.4f}")
            report_lines.append(f"- **Precision@K:** {m['retrieval']['precision_at_k']:.4f}")
            report_lines.append(f"- **MRR:** {m['retrieval']['mrr']:.4f}")
            report_lines.append(f"- **nDCG:** {m['retrieval']['ndcg']:.4f}")
            
            report_lines.append("\n#### Per-Condition Metrics")
            report_lines.append("| Condition | Precision | Recall | F1 Score |")
            report_lines.append("|---|---|---|---|")
            for condition, per_c in m['per_condition'].items():
                report_lines.append(f"| {condition} | {per_c['precision']:.4f} | {per_c['recall']:.4f} | {per_c['f1']:.4f} |")
                
        report_path = os.path.join(self.exp_dir, "report.md")
        with open(report_path, "w") as f:
            f.write("\n".join(report_lines))
            
        return report_path

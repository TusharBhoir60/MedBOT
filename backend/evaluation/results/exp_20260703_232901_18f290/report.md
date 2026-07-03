# Clinical Validation & CMAR Calibration Report

**Experiment ID:** exp_20260703_232901_18f290

## Benchmark Summary
| Model | Accuracy | F1 Score | ECE | Brier Score |
|---|---|---|---|---|
| Baseline A: Rule-based | 0.7400 | 0.7419 | 0.0600 | 0.1960 |
| Baseline B: LLM-only | 0.6600 | 0.7940 | 0.1146 | 0.2459 |
| Baseline C: RAG-only | 0.7400 | 0.8462 | 0.0871 | 0.1941 |
| Baseline D: CMAR + RAG | 0.8600 | 0.9286 | 0.0246 | 0.1210 |

## Detailed Metrics per Model

### Baseline A: Rule-based

#### Overall Metrics
- **Accuracy:** 0.7400
- **Precision:** 0.7507
- **Recall:** 0.7333
- **F1 Score:** 0.7419

#### Calibration
- **Expected Calibration Error (ECE):** 0.0600
- **Brier Score:** 0.1960
- **Optimal Threshold (F1):** 0.10
- **Optimal Threshold (Sensitivity):** 0.10
- **Optimal Threshold (Accuracy):** 0.10

#### Retrieval Metrics
- **Recall@K:** 0.0000
- **Precision@K:** 0.0000
- **MRR:** 0.0000
- **nDCG:** 0.0000

#### Per-Condition Metrics
| Condition | Precision | Recall | F1 Score |
|---|---|---|---|
| Hypertension | 0.9000 | 0.7500 | 0.8182 |
| Dengue | 0.6471 | 0.9167 | 0.7586 |
| Malaria | 0.7778 | 0.5833 | 0.6667 |
| Emergency (Cardiac) | 0.5714 | 0.6667 | 0.6154 |
| Anemia | 0.8571 | 0.7500 | 0.8000 |

### Baseline B: LLM-only

#### Overall Metrics
- **Accuracy:** 0.6600
- **Precision:** 1.0000
- **Recall:** 0.6583
- **F1 Score:** 0.7940

#### Calibration
- **Expected Calibration Error (ECE):** 0.1146
- **Brier Score:** 0.2459
- **Optimal Threshold (F1):** 0.62
- **Optimal Threshold (Sensitivity):** 0.10
- **Optimal Threshold (Accuracy):** 0.62

#### Retrieval Metrics
- **Recall@K:** 0.0000
- **Precision@K:** 0.0000
- **MRR:** 0.0000
- **nDCG:** 0.0000

#### Per-Condition Metrics
| Condition | Precision | Recall | F1 Score |
|---|---|---|---|
| Hypertension | 1.0000 | 0.5833 | 0.7368 |
| Dengue | 1.0000 | 0.6667 | 0.8000 |
| Malaria | 1.0000 | 0.7500 | 0.8571 |
| Emergency (Cardiac) | 1.0000 | 0.6667 | 0.8000 |
| Anemia | 1.0000 | 0.6250 | 0.7692 |

### Baseline C: RAG-only

#### Overall Metrics
- **Accuracy:** 0.7400
- **Precision:** 1.0000
- **Recall:** 0.7333
- **F1 Score:** 0.8462

#### Calibration
- **Expected Calibration Error (ECE):** 0.0871
- **Brier Score:** 0.1941
- **Optimal Threshold (F1):** 0.71
- **Optimal Threshold (Sensitivity):** 0.10
- **Optimal Threshold (Accuracy):** 0.71

#### Retrieval Metrics
- **Recall@K:** 0.7400
- **Precision@K:** 0.2960
- **MRR:** 0.7400
- **nDCG:** 0.7400

#### Per-Condition Metrics
| Condition | Precision | Recall | F1 Score |
|---|---|---|---|
| Hypertension | 1.0000 | 0.9167 | 0.9565 |
| Dengue | 1.0000 | 0.9167 | 0.9565 |
| Malaria | 1.0000 | 0.5000 | 0.6667 |
| Emergency (Cardiac) | 1.0000 | 0.8333 | 0.9091 |
| Anemia | 1.0000 | 0.5000 | 0.6667 |

### Baseline D: CMAR + RAG

#### Overall Metrics
- **Accuracy:** 0.8600
- **Precision:** 1.0000
- **Recall:** 0.8667
- **F1 Score:** 0.9286

#### Calibration
- **Expected Calibration Error (ECE):** 0.0246
- **Brier Score:** 0.1210
- **Optimal Threshold (F1):** 0.10
- **Optimal Threshold (Sensitivity):** 0.10
- **Optimal Threshold (Accuracy):** 0.10

#### Retrieval Metrics
- **Recall@K:** 0.8600
- **Precision@K:** 0.3440
- **MRR:** 0.8600
- **nDCG:** 0.8600

#### Per-Condition Metrics
| Condition | Precision | Recall | F1 Score |
|---|---|---|---|
| Hypertension | 1.0000 | 0.7500 | 0.8571 |
| Dengue | 1.0000 | 0.9167 | 0.9565 |
| Malaria | 1.0000 | 0.9167 | 0.9565 |
| Emergency (Cardiac) | 1.0000 | 1.0000 | 1.0000 |
| Anemia | 1.0000 | 0.7500 | 0.8571 |
# Clinical Validation & CMAR Calibration Report

**Experiment ID:** exp_20260703_192407_331620

## Benchmark Summary
| Model | Accuracy | F1 Score | ECE | Brier Score |
|---|---|---|---|---|
| Baseline A: Rule-based | 0.6800 | 0.8235 | 0.2320 | 0.0560 |
| Baseline B: LLM-only | 0.6600 | 0.7755 | 0.0709 | 0.2278 |
| Baseline C: RAG-only | 0.8200 | 0.9041 | 0.0422 | 0.1427 |
| Baseline D: CMAR + RAG | 0.9000 | 0.9565 | 0.0385 | 0.0836 |

## Detailed Metrics per Model

### Baseline A: Rule-based

#### Overall Metrics
- **Accuracy:** 0.6800
- **Precision:** 1.0000
- **Recall:** 0.7000
- **F1 Score:** 0.8235

#### Calibration
- **Expected Calibration Error (ECE):** 0.2320
- **Brier Score:** 0.0560
- **Optimal Threshold (F1):** 0.30
- **Optimal Threshold (Sensitivity):** 0.10
- **Optimal Threshold (Accuracy):** 0.30

#### Retrieval Metrics
- **Recall@K:** 0.0000
- **Precision@K:** 0.0000
- **MRR:** 0.0000
- **nDCG:** 0.0000

#### Per-Condition Metrics
| Condition | Precision | Recall | F1 Score |
|---|---|---|---|
| Anemia | 1.0000 | 0.7500 | 0.8571 |
| Hypertension | 1.0000 | 0.7500 | 0.8571 |
| Dengue | 1.0000 | 0.8333 | 0.9091 |
| Emergency (Cardiac) | 1.0000 | 0.8333 | 0.9091 |
| Malaria | 1.0000 | 0.3333 | 0.5000 |

### Baseline B: LLM-only

#### Overall Metrics
- **Accuracy:** 0.6600
- **Precision:** 1.0000
- **Recall:** 0.6333
- **F1 Score:** 0.7755

#### Calibration
- **Expected Calibration Error (ECE):** 0.0709
- **Brier Score:** 0.2278
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
| Anemia | 1.0000 | 0.5000 | 0.6667 |
| Hypertension | 1.0000 | 0.7500 | 0.8571 |
| Dengue | 1.0000 | 0.5833 | 0.7368 |
| Emergency (Cardiac) | 1.0000 | 0.5000 | 0.6667 |
| Malaria | 1.0000 | 0.8333 | 0.9091 |

### Baseline C: RAG-only

#### Overall Metrics
- **Accuracy:** 0.8200
- **Precision:** 1.0000
- **Recall:** 0.8250
- **F1 Score:** 0.9041

#### Calibration
- **Expected Calibration Error (ECE):** 0.0422
- **Brier Score:** 0.1427
- **Optimal Threshold (F1):** 0.10
- **Optimal Threshold (Sensitivity):** 0.10
- **Optimal Threshold (Accuracy):** 0.10

#### Retrieval Metrics
- **Recall@K:** 0.8200
- **Precision@K:** 0.3280
- **MRR:** 0.8200
- **nDCG:** 0.8200

#### Per-Condition Metrics
| Condition | Precision | Recall | F1 Score |
|---|---|---|---|
| Anemia | 1.0000 | 0.8750 | 0.9333 |
| Hypertension | 1.0000 | 0.8333 | 0.9091 |
| Dengue | 1.0000 | 0.7500 | 0.8571 |
| Emergency (Cardiac) | 1.0000 | 0.8333 | 0.9091 |
| Malaria | 1.0000 | 0.8333 | 0.9091 |

### Baseline D: CMAR + RAG

#### Overall Metrics
- **Accuracy:** 0.9000
- **Precision:** 1.0000
- **Recall:** 0.9167
- **F1 Score:** 0.9565

#### Calibration
- **Expected Calibration Error (ECE):** 0.0385
- **Brier Score:** 0.0836
- **Optimal Threshold (F1):** 0.10
- **Optimal Threshold (Sensitivity):** 0.10
- **Optimal Threshold (Accuracy):** 0.10

#### Retrieval Metrics
- **Recall@K:** 0.9000
- **Precision@K:** 0.3600
- **MRR:** 0.9000
- **nDCG:** 0.9000

#### Per-Condition Metrics
| Condition | Precision | Recall | F1 Score |
|---|---|---|---|
| Anemia | 1.0000 | 1.0000 | 1.0000 |
| Hypertension | 1.0000 | 0.9167 | 0.9565 |
| Dengue | 1.0000 | 0.8333 | 0.9091 |
| Emergency (Cardiac) | 1.0000 | 1.0000 | 1.0000 |
| Malaria | 1.0000 | 0.8333 | 0.9091 |
# Evaluation Metrics — AarogyaAgent CMAR

This document defines the formal evaluation metrics for the AarogyaAgent medical AI system. These metrics will be used to benchmark system quality, inform tuning, and satisfy audit requirements.

---

## 1. Precision

**Definition:** Of all conditions the system suggests as diagnoses, what fraction are clinically correct?

```
Precision = True Positives / (True Positives + False Positives)
```

**Target:** ≥ 0.80 for primary diagnosis, ≥ 0.70 for differential diagnoses.

---

## 2. Recall

**Definition:** Of all actual conditions present in the ground-truth dataset, what fraction does the system correctly identify?

```
Recall = True Positives / (True Positives + False Negatives)
```

**Target:** ≥ 0.85 — missing a real condition is clinically dangerous.

---

## 3. F1 Score

**Definition:** Harmonic mean of Precision and Recall. Balances both false positives and false negatives.

```
F1 = 2 × (Precision × Recall) / (Precision + Recall)
```

**Target:** ≥ 0.80 overall.

---

## 4. Triage Accuracy

**Definition:** Fraction of cases where the system assigns the correct urgency level (routine / urgent / emergency).

```
Triage Accuracy = Correct Urgency Assignments / Total Cases
```

**Target:** ≥ 0.90 — incorrect triage has direct patient safety implications.

**Special attention:** Emergency cases must never be classified as routine (zero-tolerance policy).

---

## 5. Confidence Calibration

**Definition:** Measures how well the system's self-reported confidence aligns with its actual accuracy.

**Method:**
- Bin predictions by confidence score (e.g., 0.0–0.1, 0.1–0.2, …, 0.9–1.0).
- For each bin, compute the actual accuracy (fraction of correct predictions).
- A perfectly calibrated system has accuracy = confidence in every bin.

**Metrics:**
- **Expected Calibration Error (ECE):** Weighted average of |accuracy − confidence| across bins.
- **Maximum Calibration Error (MCE):** Largest |accuracy − confidence| in any single bin.

**Targets:**
- ECE ≤ 0.10
- MCE ≤ 0.20

---

## 6. Retrieval Quality (RAG-specific)

| Metric | Definition | Target |
|---|---|---|
| Retrieval Precision@k | Fraction of top-k retrieved documents that are relevant | ≥ 0.70 |
| Retrieval Recall@k | Fraction of all relevant documents that appear in top-k | ≥ 0.80 |
| Mean Reciprocal Rank (MRR) | Average of 1/rank of the first relevant document | ≥ 0.75 |

---

## 7. CMAR-Specific Metrics

| Metric | Definition |
|---|---|
| Agent Agreement Rate | Fraction of cases where all agents agree on the primary condition |
| Confidence Spread | Standard deviation of per-agent confidence scores (lower = more consensus) |
| Escalation Precision | Of all cases escalated to human, fraction that truly required human review |

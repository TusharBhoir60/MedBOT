"""Builds a concise, structured reasoning summary from DiagnosisAgent output."""
from typing import Any, Dict, List


class ReasoningBuilder:
    """Converts raw clinical reasoning text into a structured summary."""

    def build(self, diagnosis_output: Dict[str, Any]) -> str:
        """
        Returns a plain-English paragraph summarising the clinical reasoning.
        Pulls from `reasoning` field and `differential_diagnoses`.
        """
        reasoning = diagnosis_output.get("reasoning", "").strip()
        primary = diagnosis_output.get("primary_diagnosis", "Unknown")
        diffs = diagnosis_output.get("differential_diagnoses", [])
        urgency = diagnosis_output.get("urgency_level", "unknown")

        lines: List[str] = []

        if reasoning:
            # Limit to first 3 sentences for a concise summary
            sentences = [s.strip() for s in reasoning.split(".") if s.strip()]
            lines.append(". ".join(sentences[:3]) + ".")

        lines.append(f"The most likely diagnosis is {primary} (urgency: {urgency}).")

        if diffs:
            diff_list = ", ".join(diffs[:3])
            lines.append(f"Other conditions considered: {diff_list}.")

        return " ".join(lines)

"""Formats retrieved evidence and citations into human-readable bullet points."""
from typing import Any, Dict, List


class EvidenceFormatter:
    """Converts raw citations and context into structured evidence bullets."""

    def format_bullets(self, diagnosis_output: Dict[str, Any]) -> List[str]:
        """
        Returns a list of bullet-point evidence strings derived from
        citations and retrieval confidence.
        """
        citations = diagnosis_output.get("citations", [])
        retrieval_conf = diagnosis_output.get("retrieval_confidence", 0.0)
        primary = diagnosis_output.get("primary_diagnosis", "this condition")

        bullets: List[str] = []

        if not citations:
            bullets.append(
                f"No specific guidelines were retrieved for {primary}; "
                "reasoning is based on clinical knowledge."
            )
            return bullets

        for i, citation in enumerate(citations[:5], 1):
            bullets.append(f"[{i}] Supporting evidence from: {citation}")

        conf_pct = int(retrieval_conf * 100)
        bullets.append(
            f"Overall retrieval relevance: {conf_pct}% — "
            + ("strong evidence base." if retrieval_conf >= 0.7
               else "moderate evidence base." if retrieval_conf >= 0.4
               else "limited evidence base; clinical judgement required.")
        )

        return bullets

    def format_citations(self, citations: List[str]) -> List[str]:
        """Formats raw citation IDs/paths into display strings."""
        formatted = []
        for i, cit in enumerate(citations, 1):
            # Strip file extensions and clean up source path
            display = cit.split("/")[-1].replace("_", " ").replace(".pdf", "").replace(".txt", "")
            display = display.strip().title()
            formatted.append(f"[{i}] {display}")
        return formatted

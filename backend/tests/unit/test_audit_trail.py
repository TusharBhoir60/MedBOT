import pytest
from ai_engine.audit.audit_trail import AuditTrailBuilder
from ai_engine.state import ConfidenceSchema

def test_audit_trail_builder_with_confidence_schema():
    builder = AuditTrailBuilder()
    
    scores = {
        "diagnosis": ConfidenceSchema(
            score=0.8,
            source="diagnosis",
            reasoning="Reasoning",
            requires_followup=False,
            requires_human=False
        ),
        "retrieval": 0.9,
        "other": {"score": 0.75}
    }
    
    trail = builder.build(
        session_id="sess-123",
        confidence_scores=scores,
        citations=["doc1", "doc2"],
        experiment_id="exp-1",
        dataset_version="v2",
        embedding_model="text-embedding-3-small",
        retrieval_top_k=5
    )
    
    assert trail.session_id == "sess-123"
    assert trail.experiment_id == "exp-1"
    assert trail.dataset_version == "v2"
    assert trail.embedding_model == "text-embedding-3-small"
    assert trail.retrieval_top_k == 5
    
    # Check score normalization
    assert trail.confidence_scores_snapshot["diagnosis"] == 0.8
    assert trail.confidence_scores_snapshot["retrieval"] == 0.9
    assert trail.confidence_scores_snapshot["other"] == 0.75
    
    # Check citations
    assert trail.retrieved_evidence_ids == ["doc1", "doc2"]
    
    # Check timestamps and versions
    assert "generated_at" in trail.timestamps
    assert trail.workflow_version == "v1"

from typing import List, Optional, Any, Dict
from datetime import datetime, timezone
from pydantic import Field
from schemas.base_schema import BaseSchema


class OverviewMetricsResponse(BaseSchema):
    total_conversations: int = 0
    total_review_tasks: int = 0
    pending_reviews: int = 0
    assigned_reviews: int = 0
    under_review: int = 0
    approved_reviews: int = 0
    rejected_reviews: int = 0
    overridden_reviews: int = 0
    closed_reviews: int = 0
    average_confidence: Optional[float] = None
    average_review_time_seconds: Optional[float] = None
    escalation_rate: Optional[float] = None
    average_messages_per_conversation: Optional[float] = None
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ConfidenceBucket(BaseSchema):
    minimum: float
    maximum: float
    count: int


class AgentAverage(BaseSchema):
    agent: str
    average: float
    sample_size: int


class ConditionAverage(BaseSchema):
    condition: str
    average: float
    sample_size: int


class ConfidenceMetricsResponse(BaseSchema):
    average_confidence: Optional[float] = None
    minimum_confidence: Optional[float] = None
    maximum_confidence: Optional[float] = None
    sample_size: int = 0
    distribution: List[ConfidenceBucket] = Field(default_factory=list)
    agent_averages: List[AgentAverage] = Field(default_factory=list)
    condition_averages: List[ConditionAverage] = Field(default_factory=list)
    low_confidence_cases: int = 0
    low_confidence_threshold: float
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class DailyThroughput(BaseSchema):
    date: str
    count: int


class ReviewMetricsResponse(BaseSchema):
    total: int = 0
    new: int = 0
    assigned: int = 0
    under_review: int = 0
    approved: int = 0
    rejected: int = 0
    overridden: int = 0
    closed: int = 0
    approval_rate: Optional[float] = None
    rejection_rate: Optional[float] = None
    override_rate: Optional[float] = None
    average_resolution_time_seconds: Optional[float] = None
    throughput: List[DailyThroughput] = Field(default_factory=list)
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class MetricCount(BaseSchema):
    name: str
    count: int


class ClinicalMetricsResponse(BaseSchema):
    top_symptoms: List[MetricCount] = Field(default_factory=list)
    top_conditions: List[MetricCount] = Field(default_factory=list)
    severity_distribution: List[MetricCount] = Field(default_factory=list)
    escalation_distribution: List[MetricCount] = Field(default_factory=list)
    sample_size: int = 0
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ActivityItem(BaseSchema):
    id: str
    type: str
    description: str
    timestamp: str


class ActivityFeedResponse(BaseSchema):
    items: List[ActivityItem] = Field(default_factory=list)
    next_cursor: Optional[str] = None
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class HealthComponent(BaseSchema):
    name: str
    status: str
    latency_ms: Optional[float] = None
    message: Optional[str] = None


class SystemHealthResponse(BaseSchema):
    overall_status: str
    components: List[HealthComponent] = Field(default_factory=list)
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

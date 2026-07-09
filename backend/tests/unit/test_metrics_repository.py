import pytest
import uuid
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

from database.base import Base
from models.chat import ChatSession
from models.review import ReviewTask, ReviewStatus
from repositories.metrics_repository import MetricsRepository
from core.config import settings

# Use in-memory sqlite for fast repo unit tests
engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

@pytest.fixture(scope="function")
async def db_session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with TestingSessionLocal() as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.mark.asyncio
async def test_empty_database_metrics(db_session: AsyncSession):
    repo = MetricsRepository(db_session)
    
    # Overview
    overview = await repo.get_overview_metrics()
    assert overview["total_conversations"] == 0
    assert overview["total_review_tasks"] == 0
    assert overview["average_confidence"] is None
    assert overview["average_review_time_seconds"] is None
    assert overview["escalation_rate"] is None
    assert overview["average_messages_per_conversation"] is None
    
    # Confidence
    conf = await repo.get_confidence_metrics(0.4)
    assert conf["average_confidence"] is None
    assert conf["sample_size"] == 0
    assert conf["low_confidence_cases"] == 0
    
    # Reviews
    reviews = await repo.get_review_metrics()
    assert reviews["total"] == 0
    assert reviews["approval_rate"] is None
    assert reviews["average_resolution_time_seconds"] is None
    
    # Clinical
    clinical = await repo.get_clinical_metrics()
    assert clinical["sample_size"] == 0
    
    # Activity
    activity = await repo.get_activity_feed()
    assert len(activity["items"]) == 0

@pytest.mark.asyncio
async def test_seeded_database_metrics(db_session: AsyncSession):
    now = datetime.now(timezone.utc)
    
    # Create chat session
    session_id = str(uuid.uuid4())
    chat = ChatSession(
        id=uuid.uuid4(),
        session_id=session_id,
        created_at=now - timedelta(days=1),
        updated_at=now,
        state={
            "messages": [{"type": "human"}, {"type": "ai"}],
            "confidence_scores": {
                "combined": {"score": 0.8},
                "intake": {"score": 0.9},
                "symptom_analysis": {"score": 0.75}
            },
            "diagnosis_output": {
                "primary_diagnosis": "Flu",
                "urgency_level": "routine"
            }
        }
    )
    db_session.add(chat)
    
    # Create another chat session with low confidence
    session_id2 = str(uuid.uuid4())
    chat2 = ChatSession(
        id=uuid.uuid4(),
        session_id=session_id2,
        created_at=now,
        updated_at=now,
        state={
            "messages": [{"type": "human"}],
            "confidence_scores": {
                "combined": {"score": 0.3},
                "intake": {"score": 0.2}
            },
            "diagnosis_output": {
                "primary_diagnosis": "Unknown",
                "urgency_level": "urgent"
            }
        }
    )
    db_session.add(chat2)
    
    # Create review task
    task = ReviewTask(
        id=uuid.uuid4(),
        session_id=session_id,
        status=ReviewStatus.APPROVED,
        created_at=now - timedelta(minutes=10),
        updated_at=now, # 10 mins resolution
        symptoms=["fever", "cough "],
        diagnosis_output={
            "primary_diagnosis": "Flu",
            "urgency_level": "routine"
        }
    )
    db_session.add(task)
    
    await db_session.commit()
    
    repo = MetricsRepository(db_session)
    
    overview = await repo.get_overview_metrics()
    assert overview["total_conversations"] == 2
    assert overview["total_review_tasks"] == 1
    assert overview["escalation_rate"] == 0.5
    assert overview["approved_reviews"] == 1
    assert abs(overview["average_review_time_seconds"] - 600) < 1.0
    
    conf = await repo.get_confidence_metrics(0.4)
    assert conf["sample_size"] == 2
    assert conf["average_confidence"] == 0.55
    assert conf["low_confidence_cases"] == 1
    
    reviews = await repo.get_review_metrics()
    assert reviews["total"] == 1
    assert reviews["approval_rate"] == 1.0
    
    clinical = await repo.get_clinical_metrics()
    assert len(clinical["top_symptoms"]) == 2
    assert clinical["top_symptoms"][0]["name"] == "Fever" or clinical["top_symptoms"][0]["name"] == "Cough"

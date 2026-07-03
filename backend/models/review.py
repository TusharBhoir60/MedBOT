from sqlalchemy import Column, String, JSON, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
import enum

from database.base import Base
from models.base_model import UUIDMixin, TimestampMixin

class ReviewStatus(str, enum.Enum):
    NEW = "NEW"
    ASSIGNED = "ASSIGNED"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    OVERRIDDEN = "OVERRIDDEN"
    REJECTED = "REJECTED"
    CLOSED = "CLOSED"

class ReviewTask(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "review_tasks"

    session_id = Column(String(50), nullable=False, unique=True)
    status = Column(Enum(ReviewStatus), default=ReviewStatus.NEW, nullable=False)
    assignee_id = Column(String(100), nullable=True) # sub from JWT
    
    # Snapshot of the state when handoff occurred
    patient_info = Column(JSON, nullable=False, default=dict)
    symptoms = Column(JSON, nullable=False, default=list)
    diagnosis_output = Column(JSON, nullable=True)
    
    # Modified/Approved final response
    final_response = Column(JSON, nullable=True)
    
    comments = relationship("ReviewComment", back_populates="task", cascade="all, delete-orphan")

class ReviewComment(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "review_comments"

    task_id = Column(PG_UUID(as_uuid=True), ForeignKey("review_tasks.id"), nullable=False)
    author_id = Column(String(100), nullable=True)
    content = Column(String(2000), nullable=False)
    
    task = relationship("ReviewTask", back_populates="comments")

from sqlalchemy import Column, String, JSON, Boolean
from database.base import Base
from models.base_model import UUIDMixin, TimestampMixin

class ChatSession(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "chat_sessions"

    session_id = Column(String(100), nullable=False, unique=True, index=True)
    patient_id = Column(String(100), nullable=True, index=True)
    title = Column(String(255), nullable=True, default="New Conversation")
    is_archived = Column(Boolean, nullable=False, default=False)
    state = Column(JSON, nullable=False, default=dict)
    metadata_info = Column(JSON, nullable=False, default=dict)

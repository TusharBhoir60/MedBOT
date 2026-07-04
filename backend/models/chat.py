from sqlalchemy import Column, String, JSON
from database.base import Base
from models.base_model import UUIDMixin, TimestampMixin

class ChatSession(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "chat_sessions"

    session_id = Column(String(100), nullable=False, unique=True, index=True)
    patient_id = Column(String(100), nullable=True, index=True)
    state = Column(JSON, nullable=False, default=dict)
    metadata_info = Column(JSON, nullable=False, default=dict)

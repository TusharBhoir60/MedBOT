from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Any, List, Optional
from datetime import datetime

class ConversationSummaryResponse(BaseModel):
    session_id: str
    title: Optional[str]
    is_archived: bool
    updated_at: datetime
    created_at: datetime
    last_message_preview: Optional[str]
    message_count: int

    model_config = ConfigDict(from_attributes=True)

class ConversationDetailResponse(BaseModel):
    session_id: str
    title: Optional[str]
    is_archived: bool
    updated_at: datetime
    created_at: datetime
    state: Dict[str, Any]

    model_config = ConfigDict(from_attributes=True)

class ConversationRenameRequest(BaseModel):
    title: str = Field(..., description="The new title for the conversation")

from pydantic import BaseModel, Field
from pydantic import field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from models.review import ReviewStatus
from schemas.base_schema import BaseSchema

class ReviewCommentCreate(BaseModel):
    content: str = Field(..., max_length=2000)

class ReviewCommentResponse(BaseSchema):
    id: str
    author_id: Optional[str] = None
    content: str

    @field_validator("id", mode="before")
    @classmethod
    def stringify_id(cls, v: Any) -> str:
        return str(v)

class ReviewTaskResponse(BaseSchema):
    id: str
    session_id: str
    status: ReviewStatus
    assignee_id: Optional[str] = None
    patient_info: Dict[str, Any]
    symptoms: List[str]
    diagnosis_output: Optional[Dict[str, Any]] = None
    final_response: Optional[Dict[str, Any]] = None
    comments: List[ReviewCommentResponse] = []

    @field_validator("id", mode="before")
    @classmethod
    def stringify_id(cls, v: Any) -> str:
        return str(v)

class ReviewTaskOverride(BaseModel):
    final_response: Dict[str, Any] = Field(..., description="The final overridden PatientResponse payload")

class ReviewRejectRequest(BaseModel):
    reason: Optional[str] = Field(None, description="Optional reason for rejection", max_length=2000)

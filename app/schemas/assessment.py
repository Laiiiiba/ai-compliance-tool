"""
Pydantic schemas for Assessment resources.
"""

from datetime import datetime
from pydantic import BaseModel, Field

from app.db.models.assessment import AssessmentStatus


class AssessmentBase(BaseModel):
    """Base schema with common assessment fields."""
    title: str = Field(..., min_length=1, max_length=255, description="Assessment title")


class AssessmentCreate(AssessmentBase):
    """Schema for creating a new assessment."""
    project_id: int = Field(..., gt=0, description="ID of the project to assess")


class AssessmentUpdate(BaseModel):
    """Schema for updating an assessment."""
    title: str | None = Field(None, min_length=1, max_length=255)
    status: AssessmentStatus | None = None


class AssessmentResponse(AssessmentBase):
    """Schema for assessment in API responses."""
    id: int
    project_id: int
    status: AssessmentStatus
    risk_level: str | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AssessmentWithDetails(AssessmentResponse):
    """Assessment with related data counts."""
    answer_count: int
    flag_count: int
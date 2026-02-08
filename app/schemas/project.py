"""
Pydantic schemas for Project resources.

These define the structure of API requests and responses.
"""

from datetime import datetime
from pydantic import BaseModel, Field


class ProjectBase(BaseModel):
    """Base schema with common project fields."""
    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    description: str | None = Field(None, description="Project description")
    organization: str | None = Field(None, max_length=255, description="Organization name")


class ProjectCreate(ProjectBase):
    """Schema for creating a new project."""
    pass


class ProjectUpdate(BaseModel):
    """Schema for updating a project (all fields optional)."""
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    organization: str | None = Field(None, max_length=255)


class ProjectResponse(ProjectBase):
    """Schema for project in API responses."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True  # Allows creating from ORM models


class ProjectWithAssessments(ProjectResponse):
    """Project with assessment count."""
    assessment_count: int
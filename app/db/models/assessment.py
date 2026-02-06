from __future__ import annotations

"""
Assessment model representing a compliance evaluation session.

An assessment is a specific evaluation of a project at a point in time.
"""

from typing import List
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base
from app.db.models.base import TimestampMixin


class AssessmentStatus(str, enum.Enum):
    """
    Status of an assessment.
    
    Workflow: draft → in_progress → completed
    """
    DRAFT = "draft"  # Created but not started
    IN_PROGRESS = "in_progress"  # User is filling it out
    COMPLETED = "completed"  # Finished and results generated
    ARCHIVED = "archived"  # Old assessment, kept for records


class Assessment(Base, TimestampMixin):
    """
    Represents a compliance assessment session for a project.
    
    A project can be assessed multiple times (e.g., after changes).
    Each assessment captures:
    - Questions answered
    - Risk levels identified
    - Regulatory flags raised
    
    Relationships:
    - Belongs to one project
    - Has many answers
    - Has many regulatory flags
    """
    
    __tablename__ = "assessments"
    
    # Primary Key
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        comment="Unique identifier for the assessment"
    )
    
    # Foreign Key to Project
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Project being assessed"
    )
    
    # Assessment Information
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Title or name of this assessment"
    )
    
    status: Mapped[AssessmentStatus] = mapped_column(
        SQLEnum(AssessmentStatus, native_enum=False),
        nullable=False,
        default=AssessmentStatus.DRAFT,
        server_default=AssessmentStatus.DRAFT.value,
        index=True,
        comment="Current status of the assessment"
    )
    
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="When the assessment was completed"
    )
    
    # Risk Assessment Results (calculated after completion)
    risk_level: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        index=True,
        comment="Overall risk level: unacceptable, high, limited, minimal"
    )
    
    # Relationships
    # Belongs to one project
    project: Mapped[Project] = relationship(
        "Project",
        back_populates="assessments"
    )
    
    # Has many answers
    answers: Mapped[List[Answer]] = relationship(
        "Answer",
        back_populates="assessment",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    # Has many regulatory flags
    regulatory_flags: Mapped[List[RegulatoryFlag]] = relationship(
        "RegulatoryFlag",
        back_populates="assessment",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<Assessment(id={self.id}, title='{self.title}', status={self.status})>"
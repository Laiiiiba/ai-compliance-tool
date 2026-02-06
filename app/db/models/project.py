from __future__ import annotations

"""
Project model representing an AI system being assessed for compliance.

A project is the main entity being evaluated (e.g., a chatbot, recommendation system).
"""

from typing import List
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.db.models.base import TimestampMixin


class Project(Base, TimestampMixin):
    """
    Represents an AI project/system undergoing compliance assessment.
    
    Examples:
    - Customer service chatbot
    - Credit scoring system
    - Recruitment screening tool
    - Medical diagnosis assistant
    
    Relationships:
    - One project can have multiple assessments over time
    """
    
    __tablename__ = "projects"
    
    # Primary Key
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        comment="Unique identifier for the project"
    )
    
    # Project Information
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,  # Index for faster searches by name
        comment="Name of the AI project"
    )
    
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Detailed description of the project and its purpose"
    )
    
    organization: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
        comment="Organization or company owning the project"
    )
    
    # Relationships
    # One project can have many assessments
    assessments: Mapped[List[Assessment]] = relationship(
        "Assessment",
        back_populates="project",
        cascade="all, delete-orphan",  # Delete assessments when project is deleted
        lazy="selectin"  # Load assessments automatically when project is loaded
    )
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<Project(id={self.id}, name='{self.name}')>"
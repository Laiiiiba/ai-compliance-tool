from __future__ import annotations

"""
RegulatoryFlag model representing identified compliance issues.

Flags are raised when assessment reveals potential compliance problems.
"""

from sqlalchemy import String, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base
from app.db.models.base import TimestampMixin


class FlagSeverity(str, enum.Enum):
    """
    Severity level of a regulatory flag.
    
    Based on EU AI Act risk categories.
    """
    CRITICAL = "critical"  # Unacceptable risk (prohibited)
    HIGH = "high"  # High-risk AI system
    MEDIUM = "medium"  # Limited risk (transparency requirements)
    LOW = "low"  # Minimal risk (no requirements)
    INFO = "info"  # Informational note


class RegulatoryFlag(Base, TimestampMixin):
    """
    Represents a compliance issue or requirement identified during assessment.
    
    Flags are raised based on deterministic rules when certain conditions are met.
    For example:
    - Using AI for credit scoring → High-risk flag
    - Processing biometric data → GDPR flag
    - Making automated decisions about employment → High-risk flag
    
    Relationships:
    - Belongs to one assessment
    """
    
    __tablename__ = "regulatory_flags"
    
    # Primary Key
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        comment="Unique identifier for the flag"
    )
    
    # Foreign Key to Assessment
    assessment_id: Mapped[int] = mapped_column(
        ForeignKey("assessments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Assessment where this flag was raised"
    )
    
    # Flag Information
    regulation: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Which regulation applies (e.g., 'EU_AI_ACT', 'GDPR')"
    )
    
    category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Category of the requirement (e.g., 'high_risk_system')"
    )
    
    severity: Mapped[FlagSeverity] = mapped_column(
        SQLEnum(FlagSeverity, native_enum=False),
        nullable=False,
        default=FlagSeverity.INFO,
        index=True,
        comment="Severity level of this flag"
    )
    
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Short title of the compliance issue"
    )
    
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Detailed explanation of the requirement or issue"
    )
    
    rule_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        comment="Identifier of the rule that raised this flag (for traceability)"
    )
    
    # Relationships
    # Belongs to one assessment
    assessment: Mapped[Assessment] = relationship(
        "Assessment",
        back_populates="regulatory_flags"
    )
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<RegulatoryFlag(id={self.id}, regulation='{self.regulation}', severity={self.severity})>"
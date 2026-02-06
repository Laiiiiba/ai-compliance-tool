from __future__ import annotations

from typing import TYPE_CHECKING

"""
Answer model representing user responses to assessment questions.
"""

from sqlalchemy import String, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.db.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.db.models.assessment import Assessment

class Answer(Base, TimestampMixin):
    """Represents a user's answer to an assessment question."""
    
    __tablename__ = "answers"
    
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        comment="Unique identifier for the answer"
    )
    
    assessment_id: Mapped[int] = mapped_column(
        ForeignKey("assessments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Assessment this answer belongs to"
    )
    
    question_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Identifier of the question being answered"
    )
    
    answer_value: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
        comment="The answer content (flexible JSON format)"
    )
    
    answer_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Plain text representation of the answer"
    )
    
    __table_args__ = (
        {
            "comment": "Stores user responses to assessment questions",
        },
    )
    
    # Relationship - KEEP STRING in relationship()
    assessment: Mapped[Assessment] = relationship(
        "Assessment",  # ← String - KEEP QUOTES
        back_populates="answers"
    )
    
    def __repr__(self) -> str:
        return f"<Answer(id={self.id}, question_id='{self.question_id}')>"
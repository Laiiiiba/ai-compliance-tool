"""
Pydantic schemas for Answer resources.
"""

from typing import Any
from pydantic import BaseModel, Field


class AnswerCreate(BaseModel):
    """Schema for submitting an answer."""
    question_id: str = Field(..., min_length=1, max_length=100, description="Question identifier")
    answer_value: Any = Field(..., description="Answer value (flexible type)")


class AnswerBatchCreate(BaseModel):
    """Schema for submitting multiple answers at once."""
    answers: list[AnswerCreate] = Field(..., min_items=1, description="List of answers")


class AnswerResponse(BaseModel):
    """Schema for answer in API responses."""
    id: int
    assessment_id: int
    question_id: str
    answer_value: dict | None
    answer_text: str | None
    
    class Config:
        from_attributes = True
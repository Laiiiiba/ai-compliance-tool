"""
Pydantic schemas for Assessment Reports.
"""

from datetime import datetime
from typing import Any
from pydantic import BaseModel


class RegulatoryFlagResponse(BaseModel):
    """Schema for regulatory flag in report."""
    regulation: str
    category: str
    severity: str
    title: str
    description: str
    rule_id: str | None


class AssessmentReportResponse(BaseModel):
    """Complete assessment report."""
    assessment: dict[str, Any]
    project: dict[str, Any]
    answers: list[dict[str, Any]]
    regulatory_flags: list[RegulatoryFlagResponse]
    summary: str
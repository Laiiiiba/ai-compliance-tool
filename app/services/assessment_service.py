"""
Assessment service for managing compliance assessments.

Orchestrates the entire assessment workflow:
1. Create assessment
2. Save answers
3. Run risk evaluation
4. Generate regulatory flags
5. Update assessment with results
"""

from __future__ import annotations
import logging
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.db.models import (
    Project,
    Assessment,
    AssessmentStatus,
    Answer,
    RegulatoryFlag,
)
from app.db.models.regulatory_flag import FlagSeverity
from app.services.risk_engine import RiskAssessmentEngine
from app.services.rules import RiskLevel


logger = logging.getLogger(__name__)


class AssessmentService:
    """
    Service for managing AI compliance assessments.
    
    Handles the complete assessment lifecycle from creation to completion.
    """
    
    def __init__(self, db: Session):
        """
        Initialize service with database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.risk_engine = RiskAssessmentEngine()
    
    def create_assessment(
        self,
        project_id: int,
        title: str
    ) -> Assessment:
        """
        Create a new assessment for a project.
        
        Args:
            project_id: ID of the project being assessed
            title: Title for this assessment
            
        Returns:
            Assessment: Created assessment
            
        Raises:
            ValueError: If project doesn't exist
        """
        # Verify project exists
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"Project with id {project_id} not found")
        
        # Create assessment
        assessment = Assessment(
            project_id=project_id,
            title=title,
            status=AssessmentStatus.DRAFT,
        )
        
        self.db.add(assessment)
        self.db.commit()
        self.db.refresh(assessment)
        
        logger.info(
            f"Created assessment {assessment.id} for project {project_id}"
        )
        
        return assessment
    
    def save_answer(
        self,
        assessment_id: int,
        question_id: str,
        answer_value: dict | str | int | bool | None,
    ) -> Answer:
        """
        Save or update an answer to an assessment question.
        
        Args:
            assessment_id: Assessment to save answer for
            question_id: Question identifier
            answer_value: The answer (can be any JSON-serializable type)
            
        Returns:
            Answer: Created or updated answer
            
        Raises:
            ValueError: If assessment doesn't exist or is completed
        """
        # Verify assessment exists and is editable
        assessment = self.db.query(Assessment).filter(
            Assessment.id == assessment_id
        ).first()
        
        if not assessment:
            raise ValueError(f"Assessment with id {assessment_id} not found")
        
        if assessment.status == AssessmentStatus.COMPLETED:
            raise ValueError("Cannot modify completed assessment")
        
        # Check if answer already exists
        existing_answer = self.db.query(Answer).filter(
            Answer.assessment_id == assessment_id,
            Answer.question_id == question_id
        ).first()
        
        if existing_answer:
            # Update existing answer
            if isinstance(answer_value, dict):
                existing_answer.answer_value = answer_value
                existing_answer.answer_text = str(answer_value)
            else:
                existing_answer.answer_value = {"value": answer_value}
                existing_answer.answer_text = str(answer_value)
            
            answer = existing_answer
            logger.info(f"Updated answer for question {question_id}")
        else:
            # Create new answer
            if isinstance(answer_value, dict):
                answer = Answer(
                    assessment_id=assessment_id,
                    question_id=question_id,
                    answer_value=answer_value,
                    answer_text=str(answer_value)
                )
            else:
                answer = Answer(
                    assessment_id=assessment_id,
                    question_id=question_id,
                    answer_value={"value": answer_value},
                    answer_text=str(answer_value)
                )
            
            self.db.add(answer)
            logger.info(f"Created answer for question {question_id}")
        
        # Update assessment status to in_progress if it was draft
        if assessment.status == AssessmentStatus.DRAFT:
            assessment.status = AssessmentStatus.IN_PROGRESS
        
        self.db.commit()
        self.db.refresh(answer)
        
        return answer
    
    def complete_assessment(self, assessment_id: int) -> Assessment:
        """
        Complete an assessment and run risk evaluation.
        
        This:
        1. Collects all answers
        2. Runs risk engine
        3. Creates regulatory flags
        4. Updates assessment with risk level
        5. Marks assessment as completed
        
        Args:
            assessment_id: Assessment to complete
            
        Returns:
            Assessment: Completed assessment with results
            
        Raises:
            ValueError: If assessment doesn't exist or has no answers
        """
        # Get assessment with relationships
        assessment = self.db.query(Assessment).filter(
            Assessment.id == assessment_id
        ).first()
        
        if not assessment:
            raise ValueError(f"Assessment with id {assessment_id} not found")
        
        if assessment.status == AssessmentStatus.COMPLETED:
            logger.warning(f"Assessment {assessment_id} is already completed")
            return assessment
        
        # Get all answers
        answers = self.db.query(Answer).filter(
            Answer.assessment_id == assessment_id
        ).all()
        
        if not answers:
            raise ValueError("Cannot complete assessment without answers")
        
        logger.info(
            f"Completing assessment {assessment_id} with {len(answers)} answers"
        )
        
        # Convert answers to format expected by risk engine
        answer_dict = self._prepare_answers_for_evaluation(answers)
        
        # Run risk evaluation
        risk_level, rule_results = self.risk_engine.evaluate_assessment(answer_dict)
        
        logger.info(f"Risk evaluation complete: {risk_level.value}")
        
        # Create regulatory flags for triggered rules
        triggered_rules = self.risk_engine.get_triggered_rules(rule_results)
        
        for result in triggered_rules:
            flag = RegulatoryFlag(
                assessment_id=assessment_id,
                regulation=result.rule.regulation,
                category=result.rule.category.value,
                severity=self._map_risk_to_severity(result.rule.risk_level),
                title=result.rule.name,
                description=result.rule.description,
                rule_id=result.rule.rule_id,
            )
            self.db.add(flag)
        
        logger.info(f"Created {len(triggered_rules)} regulatory flags")
        
        # Update assessment
        assessment.risk_level = risk_level.value
        assessment.status = AssessmentStatus.COMPLETED
        assessment.completed_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(assessment)
        
        logger.info(f"Assessment {assessment_id} completed successfully")
        
        return assessment
    
    def get_assessment_report(self, assessment_id: int) -> dict[str, Any]:
        """
        Generate a comprehensive assessment report.
        
        Args:
            assessment_id: Assessment to generate report for
            
        Returns:
            dict: Complete assessment report
            
        Raises:
            ValueError: If assessment doesn't exist
        """
        assessment = self.db.query(Assessment).filter(
            Assessment.id == assessment_id
        ).first()
        
        if not assessment:
            raise ValueError(f"Assessment with id {assessment_id} not found")
        
        # Get all related data
        answers = self.db.query(Answer).filter(
            Answer.assessment_id == assessment_id
        ).all()
        
        flags = self.db.query(RegulatoryFlag).filter(
            RegulatoryFlag.assessment_id == assessment_id
        ).all()
        
        # Build report
        report = {
            "assessment": {
                "id": assessment.id,
                "title": assessment.title,
                "status": assessment.status.value,
                "risk_level": assessment.risk_level,
                "created_at": assessment.created_at.isoformat(),
                "completed_at": (
                    assessment.completed_at.isoformat()
                    if assessment.completed_at
                    else None
                ),
            },
            "project": {
                "id": assessment.project.id,
                "name": assessment.project.name,
                "organization": assessment.project.organization,
            },
            "answers": [
                {
                    "question_id": answer.question_id,
                    "answer_text": answer.answer_text,
                    "answer_value": answer.answer_value,
                }
                for answer in answers
            ],
            "regulatory_flags": [
                {
                    "regulation": flag.regulation,
                    "category": flag.category,
                    "severity": flag.severity.value,
                    "title": flag.title,
                    "description": flag.description,
                    "rule_id": flag.rule_id,
                }
                for flag in flags
            ],
            "summary": self._generate_summary(assessment, flags),
        }
        
        return report
    
    def _prepare_answers_for_evaluation(
        self,
        answers: list[Answer]
    ) -> dict[str, Any]:
        """
        Convert Answer objects to dict format for risk engine.
        
        Args:
            answers: List of Answer objects
            
        Returns:
            dict: question_id -> answer_value mapping
        """
        answer_dict = {}
        
        for answer in answers:
            # Extract value from JSON structure
            if answer.answer_value and "value" in answer.answer_value:
                answer_dict[answer.question_id] = answer.answer_value["value"]
            elif answer.answer_value:
                answer_dict[answer.question_id] = answer.answer_value
            else:
                answer_dict[answer.question_id] = answer.answer_text
        
        return answer_dict
    
    def _map_risk_to_severity(self, risk_level: RiskLevel) -> FlagSeverity:
        """
        Map risk level to flag severity.
        
        Args:
            risk_level: Risk level from rule
            
        Returns:
            FlagSeverity: Corresponding severity
        """
        mapping = {
            RiskLevel.UNACCEPTABLE: FlagSeverity.CRITICAL,
            RiskLevel.HIGH: FlagSeverity.HIGH,
            RiskLevel.LIMITED: FlagSeverity.MEDIUM,
            RiskLevel.MINIMAL: FlagSeverity.LOW,
        }
        return mapping.get(risk_level, FlagSeverity.INFO)
    
    def _generate_summary(
        self,
        assessment: Assessment,
        flags: list[RegulatoryFlag]
    ) -> str:
        """
        Generate human-readable summary of assessment results.
        
        Args:
            assessment: Assessment object
            flags: List of regulatory flags
            
        Returns:
            str: Summary text
        """
        if not assessment.risk_level:
            return "Assessment not yet completed."
        
        risk_level = assessment.risk_level.upper()
        flag_count = len(flags)
        
        summary_parts = [
            f"Risk Level: {risk_level}",
            f"Regulatory Flags: {flag_count}",
        ]
        
        if flags:
            regulations = set(flag.regulation for flag in flags)
            summary_parts.append(
                f"Applicable Regulations: {', '.join(regulations)}"
            )
        
        return " | ".join(summary_parts)
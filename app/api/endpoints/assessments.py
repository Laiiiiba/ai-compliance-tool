"""
API endpoints for Assessment resources.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.db.models import Assessment, Answer, RegulatoryFlag
from app.schemas.assessment import (
    AssessmentCreate,
    AssessmentUpdate,
    AssessmentResponse,
    AssessmentWithDetails,
)
from app.schemas.answer import AnswerCreate, AnswerBatchCreate, AnswerResponse
from app.schemas.report import AssessmentReportResponse
from app.services.assessment_service import AssessmentService


router = APIRouter(prefix="/assessments", tags=["assessments"])


@router.post(
    "/",
    response_model=AssessmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new assessment"
)
def create_assessment(
    assessment_data: AssessmentCreate,
    db: Session = Depends(get_db)
) -> Assessment:
    """
    Create a new compliance assessment for a project.
    
    **Required fields:**
    - project_id: ID of the project to assess
    - title: Assessment title
    """
    service = AssessmentService(db)
    
    try:
        assessment = service.create_assessment(
            project_id=assessment_data.project_id,
            title=assessment_data.title
        )
        return assessment
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get(
    "/",
    response_model=list[AssessmentWithDetails],
    summary="List all assessments"
)
def list_assessments(
    project_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> list[dict]:
    """
    Get a list of assessments.
    
    **Query parameters:**
    - project_id: Filter by project (optional)
    - skip: Number of records to skip
    - limit: Maximum number of records to return
    """
    query = db.query(Assessment)
    
    if project_id:
        query = query.filter(Assessment.project_id == project_id)
    
    assessments = query.offset(skip).limit(limit).all()
    
    # Add counts
    result = []
    for assessment in assessments:
        assessment_dict = {
            "id": assessment.id,
            "project_id": assessment.project_id,
            "title": assessment.title,
            "status": assessment.status,
            "risk_level": assessment.risk_level,
            "completed_at": assessment.completed_at,
            "created_at": assessment.created_at,
            "updated_at": assessment.updated_at,
            "answer_count": len(assessment.answers),
            "flag_count": len(assessment.regulatory_flags),
        }
        result.append(assessment_dict)
    
    return result


@router.get(
    "/{assessment_id}",
    response_model=AssessmentResponse,
    summary="Get a specific assessment"
)
def get_assessment(
    assessment_id: int,
    db: Session = Depends(get_db)
) -> Assessment:
    """Get an assessment by ID."""
    assessment = db.query(Assessment).filter(
        Assessment.id == assessment_id
    ).first()
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assessment with id {assessment_id} not found"
        )
    
    return assessment


@router.post(
    "/{assessment_id}/answers",
    response_model=AnswerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit an answer"
)
def submit_answer(
    assessment_id: int,
    answer_data: AnswerCreate,
    db: Session = Depends(get_db)
) -> Answer:
    """
    Submit or update an answer for an assessment question.
    
    **Path parameters:**
    - assessment_id: Assessment to submit answer for
    
    **Request body:**
    - question_id: Question identifier
    - answer_value: The answer (any JSON-serializable value)
    """
    service = AssessmentService(db)
    
    try:
        answer = service.save_answer(
            assessment_id=assessment_id,
            question_id=answer_data.question_id,
            answer_value=answer_data.answer_value
        )
        return answer
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/{assessment_id}/answers/batch",
    response_model=list[AnswerResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Submit multiple answers at once"
)
def submit_answers_batch(
    assessment_id: int,
    batch_data: AnswerBatchCreate,
    db: Session = Depends(get_db)
) -> list[Answer]:
    """
    Submit multiple answers in a single request.
    
    **Path parameters:**
    - assessment_id: Assessment to submit answers for
    
    **Request body:**
    - answers: List of answer objects
    """
    service = AssessmentService(db)
    
    results = []
    for answer_data in batch_data.answers:
        try:
            answer = service.save_answer(
                assessment_id=assessment_id,
                question_id=answer_data.question_id,
                answer_value=answer_data.answer_value
            )
            results.append(answer)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error saving answer for {answer_data.question_id}: {str(e)}"
            )
    
    return results


@router.post(
    "/{assessment_id}/complete",
    response_model=AssessmentResponse,
    summary="Complete assessment and run risk evaluation"
)
def complete_assessment(
    assessment_id: int,
    db: Session = Depends(get_db)
) -> Assessment:
    """
    Complete an assessment and run risk evaluation.
    
    This will:
    1. Evaluate all answers against compliance rules
    2. Calculate overall risk level
    3. Generate regulatory flags
    4. Mark assessment as completed
    
    **Path parameters:**
    - assessment_id: Assessment to complete
    """
    service = AssessmentService(db)
    
    try:
        assessment = service.complete_assessment(assessment_id)
        return assessment
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/{assessment_id}/report",
    response_model=AssessmentReportResponse,
    summary="Get assessment compliance report"
)
def get_assessment_report(
    assessment_id: int,
    db: Session = Depends(get_db)
) -> dict:
    """
    Get a comprehensive compliance report for an assessment.
    
    Includes:
    - Assessment details
    - Project information
    - All answers
    - Regulatory flags
    - Compliance summary
    
    **Path parameters:**
    - assessment_id: Assessment to get report for
    """
    service = AssessmentService(db)
    
    try:
        report = service.get_assessment_report(assessment_id)
        return report
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
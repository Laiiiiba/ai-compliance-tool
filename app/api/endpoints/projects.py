"""
API endpoints for Project resources.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.db.models import Project, Assessment
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectWithAssessments,
)


router = APIRouter(prefix="/projects", tags=["projects"])


@router.post(
    "/",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new project"
)
def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db)
) -> Project:
    """
    Create a new AI project.
    
    **Required fields:**
    - name: Project name
    
    **Optional fields:**
    - description: Detailed description
    - organization: Organization name
    """
    project = Project(
        name=project_data.name,
        description=project_data.description,
        organization=project_data.organization,
    )
    
    db.add(project)
    db.commit()
    db.refresh(project)
    
    return project


@router.get(
    "/",
    response_model=list[ProjectWithAssessments],
    summary="List all projects"
)
def list_projects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> list[dict]:
    """
    Get a list of all projects with assessment counts.
    
    **Query parameters:**
    - skip: Number of records to skip (for pagination)
    - limit: Maximum number of records to return
    """
    projects = db.query(Project).offset(skip).limit(limit).all()
    
    # Add assessment count to each project
    result = []
    for project in projects:
        project_dict = {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "organization": project.organization,
            "created_at": project.created_at,
            "updated_at": project.updated_at,
            "assessment_count": len(project.assessments),
        }
        result.append(project_dict)
    
    return result


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Get a specific project"
)
def get_project(
    project_id: int,
    db: Session = Depends(get_db)
) -> Project:
    """
    Get a project by ID.
    
    **Path parameters:**
    - project_id: Unique project identifier
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )
    
    return project


@router.put(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Update a project"
)
def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: Session = Depends(get_db)
) -> Project:
    """
    Update a project's details.
    
    **Path parameters:**
    - project_id: Unique project identifier
    
    **All fields are optional** - only provided fields will be updated.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )
    
    # Update only provided fields
    update_data = project_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)
    
    db.commit()
    db.refresh(project)
    
    return project


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a project"
)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db)
) -> None:
    """
    Delete a project and all its assessments.
    
    **Warning:** This will cascade delete all assessments, answers, and flags.
    
    **Path parameters:**
    - project_id: Unique project identifier
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )
    
    db.delete(project)
    db.commit()
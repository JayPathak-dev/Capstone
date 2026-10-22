from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from backend.app.db.session import get_db
from backend.app.models.project import Project
from backend.app.models.progress_update import ProgressUpdate
from backend.app.models.milestone import Milestone
from backend.app.models.alert import Alert
from backend.app.schemas.project import (
    ProjectListItem,
    ProjectListResponse,
    ProjectDetailResponse,
    ProjectCreate,
    ProjectUpdate,
)
from backend.app.schemas.progress_update import ProgressUpdateResponse
from backend.app.schemas.milestone import MilestoneResponse
from backend.app.schemas.alert import AlertResponse
from backend.app.services.projects import (
    get_projects,
    get_project_by_id,
    create_project,
    update_project,
)
from backend.app.services.alerts import scan_and_generate_alerts

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("", response_model=ProjectListResponse)
def list_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    sector: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    risk_level: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    sort_by: str = Query("current_risk_score"),
    sort_order: str = Query("desc"),
    db: Session = Depends(get_db),
):
    """List searchable and filterable projects with pagination."""
    items, total = get_projects(
        db=db,
        skip=skip,
        limit=limit,
        search=search,
        sector=sector,
        region=region,
        risk_level=risk_level,
        status=status_filter,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    page = (skip // limit) + 1 if limit > 0 else 1
    project_items = []
    for p in items:
        # Get latest active alert if any
        latest_alert = db.scalar(
            select(Alert.title)
            .filter(Alert.project_id == p.id)
            .order_by(desc(Alert.created_at))
            .limit(1)
        )
        item_dict = {
            "id": p.id,
            "project_code": p.project_code,
            "project_name": p.project_name,
            "sector": p.sector,
            "department": p.department,
            "region": p.region,
            "implementing_agency": p.implementing_agency,
            "approved_budget": p.approved_budget,
            "revised_budget": p.revised_budget,
            "actual_expenditure": p.actual_expenditure,
            "current_physical_progress": p.current_physical_progress,
            "current_financial_progress": p.current_financial_progress,
            "planned_start_date": p.planned_start_date,
            "expected_completion_date": p.expected_completion_date,
            "project_status": p.project_status,
            "current_risk_score": p.current_risk_score,
            "current_risk_level": p.current_risk_level,
            "predicted_delay_days": p.predicted_delay_days,
            "forecast_final_cost": p.forecast_final_cost,
            "latest_alert": latest_alert,
        }
        project_items.append(ProjectListItem(**item_dict))

    return ProjectListResponse(
        total=total,
        page=page,
        page_size=limit,
        items=project_items,
    )


@router.post("", response_model=ProjectListItem, status_code=status.HTTP_201_CREATED)
def add_project(project_in: ProjectCreate, db: Session = Depends(get_db)):
    """Create a new infrastructure project sanction."""
    existing = db.scalar(
        select(Project).filter(Project.project_code == project_in.project_code)
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Project code '{project_in.project_code}' already exists",
        )

    project = create_project(db=db, project_in=project_in)
    scan_and_generate_alerts(db, project)
    return project


@router.get("/{project_id}", response_model=ProjectDetailResponse)
def get_project_details(project_id: str, db: Session = Depends(get_db)):
    """Retrieve full project details with timeline updates, milestones, and alerts."""
    project = get_project_by_id(db=db, project_id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found",
        )

    updates = [
        ProgressUpdateResponse.model_validate(u)
        for u in sorted(project.progress_updates, key=lambda x: x.reporting_date)
    ]
    milestones = [
        MilestoneResponse.model_validate(m)
        for m in sorted(project.milestones, key=lambda x: x.order_index)
    ]
    alerts = [
        AlertResponse(
            id=a.id,
            project_id=a.project_id,
            project_code=project.project_code,
            project_name=project.project_name,
            sector=project.sector,
            alert_type=a.alert_type,
            severity=a.severity,
            title=a.title,
            description=a.description,
            evidence=a.evidence,
            recommended_action=a.recommended_action,
            status=a.status,
            created_at=a.created_at,
            acknowledged_at=a.acknowledged_at,
            resolved_at=a.resolved_at,
            resolution_notes=a.resolution_notes,
        )
        for a in sorted(project.alerts, key=lambda x: x.created_at, reverse=True)
    ]

    return ProjectDetailResponse(
        id=project.id,
        project_code=project.project_code,
        project_name=project.project_name,
        sector=project.sector,
        department=project.department,
        region=project.region,
        implementing_agency=project.implementing_agency,
        approved_budget=project.approved_budget,
        revised_budget=project.revised_budget,
        actual_expenditure=project.actual_expenditure,
        current_physical_progress=project.current_physical_progress,
        current_financial_progress=project.current_financial_progress,
        planned_start_date=project.planned_start_date,
        expected_completion_date=project.expected_completion_date,
        project_status=project.project_status,
        current_risk_score=project.current_risk_score,
        current_risk_level=project.current_risk_level,
        predicted_delay_days=project.predicted_delay_days,
        forecast_final_cost=project.forecast_final_cost,
        progress_updates=updates,
        milestones=milestones,
        alerts=alerts,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


@router.patch("/{project_id}", response_model=ProjectListItem)
def patch_project(
    project_id: str,
    project_update: ProjectUpdate,
    db: Session = Depends(get_db),
):
    """Update project status, physical progress, or revised budget."""
    project = get_project_by_id(db=db, project_id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found",
        )

    updated = update_project(db=db, project=project, project_update=project_update)
    scan_and_generate_alerts(db, updated)
    return updated


@router.get("/{project_id}/timeline")
def get_project_timeline(project_id: str, db: Session = Depends(get_db)):
    """Retrieve chronological history of progress updates and milestones."""
    project = get_project_by_id(db=db, project_id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found",
        )

    updates = [
        {
            "id": u.id,
            "reporting_date": str(u.reporting_date),
            "planned_progress": u.planned_progress,
            "actual_progress": u.actual_progress,
            "cumulative_expenditure": u.cumulative_expenditure,
            "reported_issues": u.reported_issues,
            "data_source": u.data_source,
        }
        for u in sorted(project.progress_updates, key=lambda x: x.reporting_date)
    ]

    milestones = [
        {
            "id": m.id,
            "milestone_name": m.milestone_name,
            "planned_date": str(m.planned_date),
            "actual_date": str(m.actual_date) if m.actual_date else None,
            "status": m.status,
            "completion_percentage": m.completion_percentage,
            "order_index": m.order_index,
        }
        for m in sorted(project.milestones, key=lambda x: x.order_index)
    ]

    return {
        "project_id": project.id,
        "project_code": project.project_code,
        "project_name": project.project_name,
        "progress_updates": updates,
        "milestones": milestones,
    }

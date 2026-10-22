from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, func, desc, asc, or_
from backend.app.models.project import Project
from backend.app.models.alert import Alert
from backend.app.schemas.project import ProjectCreate, ProjectUpdate


def get_projects(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    search: Optional[str] = None,
    sector: Optional[str] = None,
    region: Optional[str] = None,
    risk_level: Optional[str] = None,
    status: Optional[str] = None,
    sort_by: str = "current_risk_score",
    sort_order: str = "desc",
) -> Tuple[List[Project], int]:
    """Retrieve paginated, filtered, and sorted projects."""
    query = select(Project)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Project.project_name.ilike(search_pattern),
                Project.project_code.ilike(search_pattern),
                Project.implementing_agency.ilike(search_pattern),
            )
        )

    if sector and sector != "ALL":
        query = query.filter(Project.sector == sector)

    if region and region != "ALL":
        query = query.filter(Project.region == region)

    if risk_level and risk_level != "ALL":
        query = query.filter(Project.current_risk_level == risk_level)

    if status and status != "ALL":
        query = query.filter(Project.project_status == status)

    # Count total matching
    count_query = select(func.count()).select_from(query.subquery())
    total = db.scalar(count_query) or 0

    # Sorting
    sort_column = getattr(Project, sort_by, Project.current_risk_score)
    if sort_order.lower() == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))

    query = query.offset(skip).limit(limit)
    items = db.scalars(query).all()
    return items, total


def get_project_by_id(db: Session, project_id: str) -> Optional[Project]:
    """Retrieve a project by UUID or project code."""
    query = select(Project).filter(
        or_(Project.id == project_id, Project.project_code == project_id)
    )
    return db.scalar(query)


def create_project(db: Session, project_in: ProjectCreate) -> Project:
    """Create a new infrastructure project."""
    project_dict = project_in.model_dump()
    project = Project(**project_dict)
    
    # Calculate initial financial progress
    effective_budget = project.revised_budget or project.approved_budget
    if effective_budget > 0:
        project.current_financial_progress = round(
            (project.actual_expenditure / effective_budget) * 100.0, 2
        )

    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def update_project(
    db: Session, project: Project, project_update: ProjectUpdate
) -> Project:
    """Update project details."""
    update_data = project_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)

    effective_budget = project.revised_budget or project.approved_budget
    if effective_budget > 0:
        project.current_financial_progress = round(
            (project.actual_expenditure / effective_budget) * 100.0, 2
        )

    db.commit()
    db.refresh(project)
    return project

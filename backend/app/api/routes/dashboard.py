from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.schemas.dashboard import DashboardSummaryResponse
from backend.app.services.analytics import get_dashboard_summary

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummaryResponse)
def get_summary(
    sector: Optional[str] = Query(None, description="Filter by infrastructure sector"),
    region: Optional[str] = Query(None, description="Filter by geographic region"),
    db: Session = Depends(get_db),
):
    """Retrieve executive portfolio KPIs, risk distributions, and trend analytics."""
    return get_dashboard_summary(db=db, sector=sector, region=region)

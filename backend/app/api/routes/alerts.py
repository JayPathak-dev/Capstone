from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.schemas.alert import AlertListResponse, AlertResponse, AlertUpdate
from backend.app.services.alerts import get_alerts, update_alert_status

router = APIRouter(prefix="/alerts", tags=["Early Warnings & Alerts"])


@router.get("", response_model=AlertListResponse)
def list_alerts(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    severity: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    project_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """List early warning alerts with filtering by severity, status, and project."""
    items, total = get_alerts(
        db=db,
        skip=skip,
        limit=limit,
        severity=severity,
        status=status_filter,
        project_id=project_id,
    )
    return AlertListResponse(total=total, items=items)


@router.patch("/{alert_id}", response_model=AlertResponse)
def patch_alert(
    alert_id: str,
    alert_update: AlertUpdate,
    db: Session = Depends(get_db),
):
    """Acknowledge or resolve an early warning alert."""
    if not alert_update.status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status field is required to update an alert",
        )

    alert = update_alert_status(
        db=db,
        alert_id=alert_id,
        status=alert_update.status,
        resolution_notes=alert_update.resolution_notes,
    )
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert '{alert_id}' not found",
        )

    return AlertResponse(
        id=alert.id,
        project_id=alert.project_id,
        project_code=alert.project.project_code if alert.project else "",
        project_name=alert.project.project_name if alert.project else "",
        sector=alert.project.sector if alert.project else "",
        alert_type=alert.alert_type,
        severity=alert.severity,
        title=alert.title,
        description=alert.description,
        evidence=alert.evidence,
        recommended_action=alert.recommended_action,
        status=alert.status,
        created_at=alert.created_at,
        acknowledged_at=alert.acknowledged_at,
        resolved_at=alert.resolved_at,
        resolution_notes=alert.resolution_notes,
    )

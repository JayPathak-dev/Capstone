from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select, desc, func, and_
from backend.app.models.alert import Alert
from backend.app.models.project import Project
from backend.app.models.milestone import Milestone
from backend.app.models.audit_log import AuditLog
from backend.app.schemas.alert import AlertResponse


def get_alerts(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    project_id: Optional[str] = None,
) -> Tuple[List[AlertResponse], int]:
    """Retrieve filtered early warning alerts."""
    query = select(Alert)

    if severity and severity != "ALL":
        query = query.filter(Alert.severity == severity)
    if status and status != "ALL":
        query = query.filter(Alert.status == status)
    if project_id:
        query = query.filter(Alert.project_id == project_id)

    count_query = select(func.count()).select_from(query.subquery())
    total = db.scalar(count_query) or 0

    query = query.order_by(desc(Alert.created_at)).offset(skip).limit(limit)
    alert_models = db.scalars(query).all()

    items = [
        AlertResponse(
            id=a.id,
            project_id=a.project_id,
            project_code=a.project.project_code if a.project else "",
            project_name=a.project.project_name if a.project else "",
            sector=a.project.sector if a.project else "",
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
        for a in alert_models
    ]
    return items, total


def update_alert_status(
    db: Session,
    alert_id: str,
    status: str,
    resolution_notes: Optional[str] = None,
    user_id: str = "project_officer",
) -> Optional[Alert]:
    """Acknowledge or resolve an early warning alert."""
    alert = db.get(Alert, alert_id)
    if not alert:
        return None

    now = datetime.utcnow()
    alert.status = status

    if status == "ACKNOWLEDGED":
        alert.acknowledged_at = now
    elif status in ("RESOLVED", "DISMISSED"):
        alert.resolved_at = now

    if resolution_notes:
        alert.resolution_notes = resolution_notes

    # Add audit log
    audit = AuditLog(
        action=f"ALERT_{status}",
        entity_type="ALERT",
        entity_id=alert.id,
        performed_by=user_id,
        details=f"Alert '{alert.title}' set to {status}. Notes: {resolution_notes or 'N/A'}",
    )
    db.add(audit)
    db.commit()
    db.refresh(alert)
    return alert


def scan_and_generate_alerts(db: Session, project: Project) -> List[Alert]:
    """
    Evaluate early warning detection rules for a project and create new alerts
    with duplicate suppression.
    """
    effective_budget = project.revised_budget or project.approved_budget
    burn_ratio = (project.actual_expenditure / effective_budget) if effective_budget > 0 else 0.0
    burn_pct = burn_ratio * 100.0
    progress_gap = project.current_financial_progress - project.current_physical_progress

    new_alerts: List[Alert] = []

    # Rule 1: Financial Burn Significantly Outpacing Physical Progress
    if burn_pct > 50.0 and (burn_pct - project.current_physical_progress) > 20.0:
        _create_alert_if_not_exists(
            db=db,
            project_id=project.id,
            alert_type="FINANCIAL_DIVERGENCE",
            severity="CRITICAL" if (burn_pct - project.current_physical_progress) > 30.0 else "HIGH",
            title=f"Severe Financial vs. Physical Divergence ({project.project_code})",
            description=f"Project has consumed {burn_pct:.1f}% of budget while physical progress is only {project.current_physical_progress:.1f}%.",
            evidence={
                "burn_percentage": round(burn_pct, 1),
                "physical_progress": round(project.current_physical_progress, 1),
                "gap": round(burn_pct - project.current_physical_progress, 1),
            },
            recommended_action="Freeze next contractual milestone payment tranche until independent site measurement verification.",
            collector=new_alerts,
        )

    # Rule 2: High Schedule Delay Prediction
    if project.predicted_delay_days >= 90:
        _create_alert_if_not_exists(
            db=db,
            project_id=project.id,
            alert_type="SCHEDULE_SLIPPAGE",
            severity="CRITICAL" if project.predicted_delay_days >= 180 else "HIGH",
            title=f"Critical Schedule Slippage Forecast ({project.predicted_delay_days} Days)",
            description=f"Predictive analytics forecast a completion delay of {project.predicted_delay_days} days beyond sanctioned deadline ({project.expected_completion_date}).",
            evidence={
                "predicted_delay_days": project.predicted_delay_days,
                "expected_completion_date": str(project.expected_completion_date),
            },
            recommended_action="Convene emergency Project Monitoring Committee (PMC) review to mobilize recovery catch-up schedule.",
            collector=new_alerts,
        )

    # Rule 3: Multiple Overdue Milestones
    overdue_milestones = [
        m for m in project.milestones
        if m.status in ("DELAYED", "MISSED") or (m.planned_date < datetime.utcnow().date() and m.completion_percentage < 100.0)
    ]
    if len(overdue_milestones) >= 2:
        _create_alert_if_not_exists(
            db=db,
            project_id=project.id,
            alert_type="MILESTONE_BREACH",
            severity="HIGH",
            title=f"{len(overdue_milestones)} Critical Path Milestones Overdue",
            description=f"Multiple contract milestones have missed contractual targets, including: {', '.join([m.milestone_name for m in overdue_milestones[:3]])}.",
            evidence={
                "overdue_count": len(overdue_milestones),
                "sample_milestones": [m.milestone_name for m in overdue_milestones[:3]],
            },
            recommended_action="Issue formal cure notice to EPC concessionaire demanding manpower ramp-up within 14 days.",
            collector=new_alerts,
        )

    # Rule 4: Critical Risk Score Trigger
    if project.current_risk_score >= 75.0:
        _create_alert_if_not_exists(
            db=db,
            project_id=project.id,
            alert_type="CRITICAL_RISK_BREACH",
            severity="CRITICAL",
            title=f"Composite Risk Score Breach ({project.current_risk_score:.1f}/100)",
            description=f"Composite early warning index has crossed critical threshold of 75.0, driven by multi-factor execution stress.",
            evidence={"risk_score": project.current_risk_score, "risk_level": project.current_risk_level},
            recommended_action="Escalate to Department Secretary for inter-ministerial coordination and Right-of-Way clearance.",
            collector=new_alerts,
        )

    if new_alerts:
        db.commit()

    return new_alerts


def _create_alert_if_not_exists(
    db: Session,
    project_id: str,
    alert_type: str,
    severity: str,
    title: str,
    description: str,
    evidence: Dict[str, Any],
    recommended_action: str,
    collector: List[Alert],
):
    """Suppress duplicates: don't create an alert if an active (NEW/ACKNOWLEDGED) alert exists."""
    existing = db.scalar(
        select(Alert).filter(
            and_(
                Alert.project_id == project_id,
                Alert.alert_type == alert_type,
                Alert.status.in_(["NEW", "ACKNOWLEDGED"]),
            )
        )
    )
    if not existing:
        alert = Alert(
            project_id=project_id,
            alert_type=alert_type,
            severity=severity,
            title=title,
            description=description,
            evidence=evidence,
            recommended_action=recommended_action,
            status="NEW",
        )
        db.add(alert)
        collector.append(alert)

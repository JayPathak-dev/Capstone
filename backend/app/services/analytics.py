from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import select, func, desc
from backend.app.models.project import Project
from backend.app.models.alert import Alert
from backend.app.models.progress_update import ProgressUpdate
from backend.app.schemas.dashboard import (
    DashboardSummaryResponse,
    RiskDistribution,
    SectorMetric,
    RegionMetric,
    MonthlyTrend,
)
from backend.app.schemas.alert import AlertResponse


def get_dashboard_summary(
    db: Session,
    sector: Optional[str] = None,
    region: Optional[str] = None,
) -> DashboardSummaryResponse:
    """Calculate aggregated executive portfolio metrics."""
    query = select(Project)
    if sector and sector != "ALL":
        query = query.filter(Project.sector == sector)
    if region and region != "ALL":
        query = query.filter(Project.region == region)

    projects = db.scalars(query).all()
    total_projects = len(projects)

    if total_projects == 0:
        return DashboardSummaryResponse(
            total_projects=0,
            high_critical_risk_projects=0,
            predicted_cost_overrun_projects=0,
            predicted_delay_projects=0,
            total_approved_budget=0.0,
            total_revised_budget=0.0,
            total_actual_expenditure=0.0,
            total_forecast_final_cost=0.0,
            net_cost_variance=0.0,
            average_physical_progress=0.0,
            average_financial_progress=0.0,
            risk_distribution=RiskDistribution(),
            sector_breakdown=[],
            region_breakdown=[],
            recent_alerts=[],
            monthly_trends=[],
        )

    high_crit_count = sum(1 for p in projects if p.current_risk_level in ("HIGH", "CRITICAL"))
    overrun_count = sum(1 for p in projects if p.forecast_final_cost > p.approved_budget)
    delay_count = sum(1 for p in projects if p.predicted_delay_days > 30)

    total_approved = sum(p.approved_budget for p in projects)
    total_revised = sum(p.revised_budget or p.approved_budget for p in projects)
    total_expenditure = sum(p.actual_expenditure for p in projects)
    total_forecast = sum(p.forecast_final_cost or p.approved_budget for p in projects)
    net_variance = total_forecast - total_approved

    avg_physical = sum(p.current_physical_progress for p in projects) / total_projects
    avg_financial = sum(p.current_financial_progress for p in projects) / total_projects

    # Risk Distribution
    risk_dist = RiskDistribution(
        low=sum(1 for p in projects if p.current_risk_level == "LOW"),
        moderate=sum(1 for p in projects if p.current_risk_level == "MODERATE"),
        high=sum(1 for p in projects if p.current_risk_level == "HIGH"),
        critical=sum(1 for p in projects if p.current_risk_level == "CRITICAL"),
    )

    # Sector Breakdown
    sectors_map: Dict[str, List[Project]] = {}
    for p in projects:
        sectors_map.setdefault(p.sector, []).append(p)

    sector_breakdown = [
        SectorMetric(
            sector=sec,
            count=len(plist),
            approved_budget=round(sum(p.approved_budget for p in plist), 2),
            actual_expenditure=round(sum(p.actual_expenditure for p in plist), 2),
            avg_physical_progress=round(sum(p.current_physical_progress for p in plist) / len(plist), 1),
            avg_risk_score=round(sum(p.current_risk_score for p in plist) / len(plist), 1),
            high_risk_count=sum(1 for p in plist if p.current_risk_level in ("HIGH", "CRITICAL")),
        )
        for sec, plist in sorted(sectors_map.items(), key=lambda x: len(x[1]), reverse=True)
    ]

    # Region Breakdown
    regions_map: Dict[str, List[Project]] = {}
    for p in projects:
        regions_map.setdefault(p.region, []).append(p)

    region_breakdown = [
        RegionMetric(
            region=reg,
            count=len(plist),
            approved_budget=round(sum(p.approved_budget for p in plist), 2),
            actual_expenditure=round(sum(p.actual_expenditure for p in plist), 2),
            avg_risk_score=round(sum(p.current_risk_score for p in plist) / len(plist), 1),
        )
        for reg, plist in sorted(regions_map.items(), key=lambda x: len(x[1]), reverse=True)
    ]

    # Recent Alerts
    alerts_query = (
        select(Alert)
        .order_by(desc(Alert.created_at))
        .limit(6)
    )
    alert_records = db.scalars(alerts_query).all()
    recent_alerts: List[AlertResponse] = []
    for a in alert_records:
        recent_alerts.append(
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
        )

    # Monthly Trends (aggregate recent progress updates)
    trends_query = (
        select(
            ProgressUpdate.reporting_date,
            func.avg(ProgressUpdate.planned_progress).label("avg_planned"),
            func.avg(ProgressUpdate.actual_progress).label("avg_actual"),
            func.sum(ProgressUpdate.cumulative_expenditure).label("sum_exp"),
        )
        .group_by(ProgressUpdate.reporting_date)
        .order_by(ProgressUpdate.reporting_date)
        .limit(12)
    )
    trend_rows = db.execute(trends_query).all()
    monthly_trends = [
        MonthlyTrend(
            month=r[0].strftime("%b %Y"),
            planned_progress=round(float(r[1] or 0), 1),
            actual_progress=round(float(r[2] or 0), 1),
            expenditure=round(float(r[3] or 0) / 100.0, 1),  # Scale for display
        )
        for r in trend_rows
    ]

    return DashboardSummaryResponse(
        total_projects=total_projects,
        high_critical_risk_projects=high_crit_count,
        predicted_cost_overrun_projects=overrun_count,
        predicted_delay_projects=delay_count,
        total_approved_budget=round(total_approved, 2),
        total_revised_budget=round(total_revised, 2),
        total_actual_expenditure=round(total_expenditure, 2),
        total_forecast_final_cost=round(total_forecast, 2),
        net_cost_variance=round(net_variance, 2),
        average_physical_progress=round(avg_physical, 1),
        average_financial_progress=round(avg_financial, 1),
        risk_distribution=risk_dist,
        sector_breakdown=sector_breakdown,
        region_breakdown=region_breakdown,
        recent_alerts=recent_alerts,
        monthly_trends=monthly_trends,
    )

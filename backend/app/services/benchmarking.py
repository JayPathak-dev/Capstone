import math
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from backend.app.models.project import Project
from backend.app.schemas.benchmarking import BenchmarkingResponse, PeerProjectComparison


def calculate_project_similarity(target: Project, candidate: Project) -> float:
    """
    Compute a normalized similarity score in [0.0, 1.0] between two projects
    based on sector match, budget proximity, progress stage, and region.
    """
    if target.id == candidate.id:
        return 1.0

    # Sector weight: 0.40
    sector_sim = 1.0 if target.sector == candidate.sector else 0.15

    # Budget distance weight: 0.30 (log ratio similarity)
    b1, b2 = max(1.0, target.approved_budget), max(1.0, candidate.approved_budget)
    budget_ratio = min(b1, b2) / max(b1, b2)
    budget_sim = budget_ratio

    # Progress stage weight: 0.20
    prog_diff = abs(target.current_physical_progress - candidate.current_physical_progress)
    progress_sim = max(0.0, 1.0 - (prog_diff / 100.0))

    # Region weight: 0.10
    region_sim = 1.0 if target.region == candidate.region else 0.4

    total_sim = (
        0.40 * sector_sim +
        0.30 * budget_sim +
        0.20 * progress_sim +
        0.10 * region_sim
    )
    return round(total_sim, 3)


def get_peer_benchmarking(
    db: Session,
    project_id: str,
    cohort_size: int = 5,
) -> Optional[BenchmarkingResponse]:
    """Retrieve peer benchmarking analysis for a target project."""
    target = db.scalar(
        select(Project).filter(
            (Project.id == project_id) | (Project.project_code == project_id)
        )
    )
    if not target:
        return None

    # Fetch candidate projects (prefer same sector or all projects)
    candidates = db.scalars(
        select(Project).filter(Project.id != target.id)
    ).all()

    if not candidates:
        target_peer = _to_peer(target, 1.0)
        return BenchmarkingResponse(
            target_project=target_peer,
            cohort_count=0,
            cohort_avg_budget=target.approved_budget,
            cohort_avg_progress=target.current_physical_progress,
            cohort_avg_risk_score=target.current_risk_score,
            cohort_avg_delay_days=float(target.predicted_delay_days),
            cohort_cost_overrun_rate=0.0,
            similar_projects=[],
        )

    scored_candidates = [
        (c, calculate_project_similarity(target, c))
        for c in candidates
    ]
    # Sort by highest similarity
    scored_candidates.sort(key=lambda x: x[1], reverse=True)
    top_peers = scored_candidates[:cohort_size]

    peer_comparisons = [
        _to_peer(c, sim)
        for c, sim in top_peers
    ]

    # Cohort averages
    cohort_count = len(peer_comparisons)
    cohort_avg_budget = round(sum(p.approved_budget for p in peer_comparisons) / cohort_count, 2)
    cohort_avg_progress = round(sum(p.physical_progress for p in peer_comparisons) / cohort_count, 1)
    cohort_avg_risk = round(sum(p.risk_score for p in peer_comparisons) / cohort_count, 1)
    cohort_avg_delay = round(sum(p.predicted_delay_days for p in peer_comparisons) / cohort_count, 1)
    cohort_overrun_rate = round(
        sum(1 for p in peer_comparisons if p.actual_expenditure > p.approved_budget) / cohort_count, 2
    )

    return BenchmarkingResponse(
        target_project=_to_peer(target, 1.0),
        cohort_count=cohort_count,
        cohort_avg_budget=cohort_avg_budget,
        cohort_avg_progress=cohort_avg_progress,
        cohort_avg_risk_score=cohort_avg_risk,
        cohort_avg_delay_days=cohort_avg_delay,
        cohort_cost_overrun_rate=cohort_overrun_rate,
        similar_projects=peer_comparisons,
    )


def _to_peer(p: Project, similarity: float) -> PeerProjectComparison:
    return PeerProjectComparison(
        project_id=p.id,
        project_code=p.project_code,
        project_name=p.project_name,
        sector=p.sector,
        region=p.region,
        approved_budget=p.approved_budget,
        actual_expenditure=p.actual_expenditure,
        physical_progress=p.current_physical_progress,
        financial_progress=p.current_financial_progress,
        risk_score=p.current_risk_score,
        risk_level=p.current_risk_level,
        predicted_delay_days=p.predicted_delay_days,
        similarity_score=similarity,
    )

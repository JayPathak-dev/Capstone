from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.schemas.benchmarking import BenchmarkingResponse
from backend.app.services.benchmarking import get_peer_benchmarking

router = APIRouter(prefix="/benchmarking", tags=["Peer Benchmarking"])


@router.get("", response_model=BenchmarkingResponse)
def get_benchmarking(
    project_id: str = Query(..., description="Target project ID or code to benchmark"),
    cohort_size: int = Query(5, ge=2, le=20),
    db: Session = Depends(get_db),
):
    """Retrieve peer benchmarking analysis for a target infrastructure project."""
    res = get_peer_benchmarking(db=db, project_id=project_id, cohort_size=cohort_size)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Target project '{project_id}' not found for benchmarking",
        )
    return res

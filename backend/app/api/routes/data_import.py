from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.schemas.import_data import ImportPreviewResponse, ImportCommitResponse
from backend.app.services.data_import import preview_csv_import, commit_csv_import

router = APIRouter(prefix="/data", tags=["Data Ingestion & Management"])

SAMPLE_CSV_CONTENT = """project_code,project_name,sector,department,region,implementing_agency,approved_budget,revised_budget,actual_expenditure,planned_start_date,expected_completion_date,current_physical_progress,project_status
NHAI-2024-EXP-12,Varanasi-Kolkata Expressway Pkg 3,Roads & Highways,Ministry of Road Transport,Eastern,NHAI,3200.0,3450.0,2100.0,2023-01-15,2026-06-30,42.5,IN_PROGRESS
RVNL-2024-COR-05,Rishikesh-Karanprayag Rail Link Pkg 8,Railways,Ministry of Railways,Northern,RVNL,5400.0,6100.0,4200.0,2021-04-01,2025-12-31,58.0,DELAYED
DMRC-2024-MET-09,Delhi Metro Phase IV Aerocity Line,Urban Mass Transit,Ministry of Housing and Urban Affairs,Northern,DMRC,4800.0,4800.0,1950.0,2022-09-01,2026-03-31,39.0,IN_PROGRESS
NTPC-2024-SOL-03,Khavda Solar Ultra Mega Park 1200MW,Power & Renewable Energy,Ministry of Power,Western,NTPC,6200.0,6200.0,4100.0,2022-11-01,2025-09-30,64.0,IN_PROGRESS
JJM-2024-WAT-07,Bundelkhand Rural Water Supply Grid,Water & Sanitation,Department of Drinking Water,Central,State Water Agency,1800.0,1950.0,1450.0,2022-02-15,2025-05-31,61.0,IN_PROGRESS
"""


@router.get("/sample-csv", response_class=PlainTextResponse)
def get_sample_csv():
    """Download a valid sample CSV template for infrastructure project import."""
    return PlainTextResponse(
        content=SAMPLE_CSV_CONTENT,
        headers={"Content-Disposition": "attachment; filename=paimana_projects_template.csv"},
    )


@router.post("/import/preview", response_model=ImportPreviewResponse)
async def preview_import(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Upload CSV file for dry-run validation, column verification, and error inspection."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must be a CSV file (.csv)",
        )

    content = await file.read()
    try:
        decoded_content = content.decode("utf-8")
    except UnicodeDecodeError:
        decoded_content = content.decode("latin-1")

    return preview_csv_import(db=db, csv_content=decoded_content)


@router.post("/import/commit", response_model=ImportCommitResponse)
async def commit_import(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Commit validated CSV infrastructure records into the database."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must be a CSV file (.csv)",
        )

    content = await file.read()
    try:
        decoded_content = content.decode("utf-8")
    except UnicodeDecodeError:
        decoded_content = content.decode("latin-1")

    return commit_csv_import(db=db, csv_content=decoded_content)

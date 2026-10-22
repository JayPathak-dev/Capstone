import csv
import io
from datetime import datetime, date
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select
from backend.app.models.project import Project
from backend.app.schemas.import_data import (
    ImportPreviewResponse,
    ValidationErrorItem,
    ImportCommitResponse,
)
from backend.app.ml.fallback import calculate_calibrated_risk
from backend.app.services.alerts import scan_and_generate_alerts

REQUIRED_COLUMNS = [
    "project_code",
    "project_name",
    "sector",
    "department",
    "region",
    "implementing_agency",
    "approved_budget",
    "planned_start_date",
    "expected_completion_date",
]

OPTIONAL_COLUMNS = [
    "revised_budget",
    "actual_expenditure",
    "current_physical_progress",
    "project_status",
]


def preview_csv_import(
    db: Session, csv_content: str, max_preview_rows: int = 10
) -> ImportPreviewResponse:
    """Parse and validate CSV data without modifying the database."""
    reader = csv.DictReader(io.StringIO(csv_content))
    fieldnames = [f.strip() for f in (reader.fieldnames or [])]

    # Check required columns
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in fieldnames]

    errors: List[ValidationErrorItem] = []
    preview_rows: List[Dict[str, Any]] = []
    valid_count = 0
    invalid_count = 0

    # Fetch existing project codes for duplicate check
    existing_codes = set(db.scalars(select(Project.project_code)).all())
    seen_in_file = set()

    for row_idx, raw_row in enumerate(reader, start=2):
        row = {k.strip(): (v.strip() if v else "") for k, v in raw_row.items() if k}
        row_errors: List[ValidationErrorItem] = []

        # Required field presence
        for req_col in REQUIRED_COLUMNS:
            if not row.get(req_col):
                row_errors.append(
                    ValidationErrorItem(
                        row=row_idx,
                        column=req_col,
                        value=row.get(req_col, ""),
                        message=f"Missing required field: {req_col}",
                        severity="ERROR",
                    )
                )

        # Project Code uniqueness
        pcode = row.get("project_code", "")
        if pcode:
            if pcode in seen_in_file:
                row_errors.append(
                    ValidationErrorItem(
                        row=row_idx,
                        column="project_code",
                        value=pcode,
                        message=f"Duplicate project_code '{pcode}' within CSV file",
                        severity="ERROR",
                    )
                )
            seen_in_file.add(pcode)

            if pcode in existing_codes:
                row_errors.append(
                    ValidationErrorItem(
                        row=row_idx,
                        column="project_code",
                        value=pcode,
                        message=f"Project code '{pcode}' already exists in database (will be updated)",
                        severity="WARNING",
                    )
                )

        # Budget validation
        try:
            budget = float(row.get("approved_budget", 0))
            if budget <= 0:
                row_errors.append(
                    ValidationErrorItem(
                        row=row_idx,
                        column="approved_budget",
                        value=row.get("approved_budget"),
                        message="Approved budget must be greater than 0",
                        severity="ERROR",
                    )
                )
        except (ValueError, TypeError):
            row_errors.append(
                ValidationErrorItem(
                    row=row_idx,
                    column="approved_budget",
                    value=row.get("approved_budget"),
                    message="Invalid numeric format for approved_budget",
                    severity="ERROR",
                )
            )

        # Dates validation
        start_date = None
        end_date = None
        for date_col in ["planned_start_date", "expected_completion_date"]:
            val = row.get(date_col)
            if val:
                try:
                    parsed_dt = datetime.strptime(val, "%Y-%m-%d").date()
                    if date_col == "planned_start_date":
                        start_date = parsed_dt
                    else:
                        end_date = parsed_dt
                except ValueError:
                    row_errors.append(
                        ValidationErrorItem(
                            row=row_idx,
                            column=date_col,
                            value=val,
                            message=f"Invalid date format for {date_col}. Expected YYYY-MM-DD",
                            severity="ERROR",
                        )
                    )

        if start_date and end_date and end_date <= start_date:
            row_errors.append(
                ValidationErrorItem(
                    row=row_idx,
                    column="expected_completion_date",
                    value=str(end_date),
                    message="expected_completion_date must be after planned_start_date",
                    severity="ERROR",
                )
            )

        # Physical progress validation
        phys_prog_str = row.get("current_physical_progress")
        if phys_prog_str:
            try:
                phys_prog = float(phys_prog_str)
                if not (0.0 <= phys_prog <= 100.0):
                    row_errors.append(
                        ValidationErrorItem(
                            row=row_idx,
                            column="current_physical_progress",
                            value=phys_prog_str,
                            message="Physical progress must be between 0.0 and 100.0",
                            severity="ERROR",
                        )
                    )
            except ValueError:
                row_errors.append(
                    ValidationErrorItem(
                        row=row_idx,
                        column="current_physical_progress",
                        value=phys_prog_str,
                        message="Physical progress must be a numeric float",
                        severity="ERROR",
                    )
                )

        has_blocking_errors = any(e.severity == "ERROR" for e in row_errors)
        if has_blocking_errors:
            invalid_count += 1
        else:
            valid_count += 1

        errors.extend(row_errors)
        if len(preview_rows) < max_preview_rows:
            preview_rows.append(row)

    can_commit = (len(missing_cols) == 0) and (invalid_count == 0) and (valid_count > 0)

    return ImportPreviewResponse(
        total_rows=valid_count + invalid_count,
        valid_rows=valid_count,
        invalid_rows=invalid_count,
        columns_detected=fieldnames,
        missing_required_columns=missing_cols,
        errors=errors[:100],  # cap returned errors
        preview_data=preview_rows,
        can_commit=can_commit,
    )


def commit_csv_import(db: Session, csv_content: str) -> ImportCommitResponse:
    """Commit verified CSV records to database inside a transaction."""
    reader = csv.DictReader(io.StringIO(csv_content))
    imported = 0
    skipped = 0
    messages: List[str] = []

    try:
        for row in reader:
            pcode = row.get("project_code", "").strip()
            if not pcode:
                skipped += 1
                continue

            # Check if project exists to update or insert
            project = db.scalar(select(Project).filter(Project.project_code == pcode))
            if not project:
                project = Project(project_code=pcode)
                db.add(project)

            project.project_name = row.get("project_name", "").strip()
            project.sector = row.get("sector", "").strip()
            project.department = row.get("department", "").strip()
            project.region = row.get("region", "").strip()
            project.implementing_agency = row.get("implementing_agency", "").strip()
            project.approved_budget = float(row.get("approved_budget", 0))

            rev_budget_str = row.get("revised_budget", "").strip()
            project.revised_budget = float(rev_budget_str) if rev_budget_str else None

            project.actual_expenditure = float(row.get("actual_expenditure", 0) or 0)
            project.planned_start_date = datetime.strptime(
                row.get("planned_start_date", "").strip(), "%Y-%m-%d"
            ).date()
            project.expected_completion_date = datetime.strptime(
                row.get("expected_completion_date", "").strip(), "%Y-%m-%d"
            ).date()

            project.current_physical_progress = float(
                row.get("current_physical_progress", 0) or 0
            )

            effective_budget = project.revised_budget or project.approved_budget
            if effective_budget > 0:
                project.current_financial_progress = round(
                    (project.actual_expenditure / effective_budget) * 100.0, 2
                )

            project.project_status = row.get("project_status", "IN_PROGRESS").strip()

            # Compute initial risk score
            risk = calculate_calibrated_risk(
                approved_budget=project.approved_budget,
                revised_budget=project.revised_budget,
                actual_expenditure=project.actual_expenditure,
                planned_progress=project.current_physical_progress + 5.0,
                actual_progress=project.current_physical_progress,
                planned_start_date=project.planned_start_date,
                expected_completion_date=project.expected_completion_date,
            )
            project.current_risk_score = risk["risk_score"]
            project.current_risk_level = risk["risk_level"]
            project.predicted_delay_days = risk["predicted_delay_days"]
            project.forecast_final_cost = risk["expected_final_cost"]

            imported += 1

        db.commit()

        # Generate alerts for updated projects
        all_projects = db.scalars(select(Project)).all()
        for p in all_projects:
            scan_and_generate_alerts(db, p)

        return ImportCommitResponse(
            success=True,
            imported_count=imported,
            skipped_count=skipped,
            message=f"Successfully imported {imported} infrastructure project records into PAIMANA.",
        )
    except Exception as e:
        db.rollback()
        return ImportCommitResponse(
            success=False,
            imported_count=0,
            skipped_count=skipped,
            message=f"Failed to commit import transaction: {str(e)}",
            errors=[str(e)],
        )

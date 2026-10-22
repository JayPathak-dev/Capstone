from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class ValidationErrorItem(BaseModel):
    row: int
    column: str
    value: Any
    message: str
    severity: str = "ERROR"  # ERROR, WARNING


class ImportPreviewResponse(BaseModel):
    total_rows: int
    valid_rows: int
    invalid_rows: int
    columns_detected: List[str]
    missing_required_columns: List[str]
    errors: List[ValidationErrorItem]
    preview_data: List[Dict[str, Any]]
    can_commit: bool


class ImportCommitResponse(BaseModel):
    success: bool
    imported_count: int
    skipped_count: int
    message: str
    errors: List[str] = []

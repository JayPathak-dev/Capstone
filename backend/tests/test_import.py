def test_csv_import_preview_and_commit(client):
    valid_csv = """project_code,project_name,sector,department,region,implementing_agency,approved_budget,planned_start_date,expected_completion_date,current_physical_progress
CSV-TEST-01,CSV Imported Corridor 1,Roads & Highways,MoRTH,Western,NHAI,1500.0,2023-01-01,2025-12-31,35.0
CSV-TEST-02,CSV Imported Corridor 2,Railways,MoR,Southern,RVNL,2200.0,2022-06-01,2026-06-30,48.0
"""
    # 1. Preview CSV
    files = {"file": ("test.csv", valid_csv, "text/csv")}
    preview_res = client.post("/api/v1/data/import/preview", files=files)
    assert preview_res.status_code == 200
    preview_data = preview_res.json()
    assert preview_data["valid_rows"] == 2
    assert preview_data["can_commit"] is True

    # 2. Commit CSV
    files_commit = {"file": ("test.csv", valid_csv, "text/csv")}
    commit_res = client.post("/api/v1/data/import/commit", files=files_commit)
    assert commit_res.status_code == 200
    commit_data = commit_res.json()
    assert commit_data["success"] is True
    assert commit_data["imported_count"] == 2

    # 3. Verify in database
    get_res = client.get("/api/v1/projects/CSV-TEST-01")
    assert get_res.status_code == 200
    assert get_res.json()["project_code"] == "CSV-TEST-01"

def test_create_and_get_project(client):
    payload = {
        "project_code": "TEST-2024-EXP-01",
        "project_name": "Test Greenfield Highway Corridor",
        "sector": "Roads & Highways",
        "department": "Ministry of Road Transport and Highways",
        "region": "Northern",
        "implementing_agency": "NHAI",
        "approved_budget": 2500.0,
        "planned_start_date": "2023-01-01",
        "expected_completion_date": "2025-12-31",
        "actual_expenditure": 500.0,
        "current_physical_progress": 25.0,
        "project_status": "IN_PROGRESS",
    }

    # 1. Create project
    res = client.post("/api/v1/projects", json=payload)
    assert res.status_code == 201
    created = res.json()
    assert created["project_code"] == "TEST-2024-EXP-01"
    assert created["current_financial_progress"] == 20.0
    project_id = created["id"]

    # 2. Get project by ID
    res_get = client.get(f"/api/v1/projects/{project_id}")
    assert res_get.status_code == 200
    details = res_get.json()
    assert details["project_name"] == "Test Greenfield Highway Corridor"

    # 3. List projects with filter
    res_list = client.get("/api/v1/projects?sector=Roads%20%26%20Highways")
    assert res_list.status_code == 200
    list_data = res_list.json()
    assert list_data["total"] >= 1


def test_duplicate_project_code_rejection(client):
    payload = {
        "project_code": "DUP-2024-01",
        "project_name": "First Instance",
        "sector": "Railways",
        "department": "Ministry of Railways",
        "region": "Western",
        "implementing_agency": "RVNL",
        "approved_budget": 1000.0,
        "planned_start_date": "2023-01-01",
        "expected_completion_date": "2024-12-31",
    }
    res1 = client.post("/api/v1/projects", json=payload)
    assert res1.status_code == 201

    # Second creation must fail
    res2 = client.post("/api/v1/projects", json=payload)
    assert res2.status_code == 400
    assert "already exists" in res2.json()["detail"]


def test_invalid_budget_validation(client):
    payload = {
        "project_code": "INV-2024-01",
        "project_name": "Negative Budget Project",
        "sector": "Water & Sanitation",
        "department": "Jal Shakti",
        "region": "Central",
        "implementing_agency": "State Agency",
        "approved_budget": -500.0,  # invalid
        "planned_start_date": "2023-01-01",
        "expected_completion_date": "2024-12-31",
    }
    res = client.post("/api/v1/projects", json=payload)
    assert res.status_code == 422

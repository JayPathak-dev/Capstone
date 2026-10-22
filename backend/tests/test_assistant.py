def test_assistant_chat_grounding(client):
    # Pre-create a known project
    p = {
        "project_code": "ASST-TEST-01",
        "project_name": "Grounded Expressway Link",
        "sector": "Roads & Highways",
        "department": "MoRTH",
        "region": "Northern",
        "implementing_agency": "NHAI",
        "approved_budget": 5000.0,
        "planned_start_date": "2022-01-01",
        "expected_completion_date": "2025-12-31",
        "actual_expenditure": 4200.0,
        "current_physical_progress": 45.0,
    }
    client.post("/api/v1/projects", json=p)

    # Ask about the project
    chat_payload = {"message": "Tell me about ASST-TEST-01"}
    res = client.post("/api/v1/assistant/chat", json=chat_payload)
    assert res.status_code == 200
    data = res.json()
    assert "Grounded Expressway Link" in data["response"]
    assert "get_project_details" in data["tools_used"]
    assert len(data["referenced_projects"]) == 1
    assert data["referenced_projects"][0]["project_code"] == "ASST-TEST-01"


def test_assistant_high_risk_query(client):
    chat_payload = {"message": "Which projects have the highest risk?"}
    res = client.post("/api/v1/assistant/chat", json=chat_payload)
    assert res.status_code == 200
    data = res.json()
    assert "list_high_risk_projects" in data["tools_used"]

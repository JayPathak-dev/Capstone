def test_alerts_lifecycle(client):
    # Create project with high divergence to trigger alert
    payload = {
        "project_code": "ALERT-TEST-01",
        "project_name": "High Burn Lagging Progress Project",
        "sector": "Roads & Highways",
        "department": "MoRTH",
        "region": "Northern",
        "implementing_agency": "NHAI",
        "approved_budget": 1000.0,
        "planned_start_date": "2022-01-01",
        "expected_completion_date": "2024-12-31",
        "actual_expenditure": 750.0,  # 75% burn
        "current_physical_progress": 20.0,  # 20% physical -> 55% gap
        "project_status": "DELAYED",
    }
    create_res = client.post("/api/v1/projects", json=payload)
    assert create_res.status_code == 201

    # List alerts
    alerts_res = client.get("/api/v1/alerts")
    assert alerts_res.status_code == 200
    alerts_data = alerts_res.json()
    assert alerts_data["total"] >= 1

    first_alert = alerts_data["items"][0]
    alert_id = first_alert["id"]
    assert first_alert["status"] == "NEW"

    # Acknowledge alert
    ack_res = client.patch(
        f"/api/v1/alerts/{alert_id}",
        json={"status": "ACKNOWLEDGED", "resolution_notes": "Project Director notified."},
    )
    assert ack_res.status_code == 200
    assert ack_res.json()["status"] == "ACKNOWLEDGED"

    # Resolve alert
    res_res = client.patch(
        f"/api/v1/alerts/{alert_id}",
        json={"status": "RESOLVED", "resolution_notes": "Contractor remobilized."},
    )
    assert res_res.status_code == 200
    assert res_res.json()["status"] == "RESOLVED"

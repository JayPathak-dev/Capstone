def test_benchmarking_peer_generation(client):
    # Create two projects in same sector
    p1 = {
        "project_code": "BENCH-01",
        "project_name": "Delhi Expressway A",
        "sector": "Roads & Highways",
        "department": "MoRTH",
        "region": "Northern",
        "implementing_agency": "NHAI",
        "approved_budget": 3000.0,
        "planned_start_date": "2022-01-01",
        "expected_completion_date": "2025-12-31",
        "actual_expenditure": 1200.0,
        "current_physical_progress": 40.0,
    }
    p2 = {
        "project_code": "BENCH-02",
        "project_name": "Agra Expressway B",
        "sector": "Roads & Highways",
        "department": "MoRTH",
        "region": "Northern",
        "implementing_agency": "NHAI",
        "approved_budget": 3200.0,
        "planned_start_date": "2022-02-01",
        "expected_completion_date": "2025-11-30",
        "actual_expenditure": 1300.0,
        "current_physical_progress": 42.0,
    }

    client.post("/api/v1/projects", json=p1)
    client.post("/api/v1/projects", json=p2)

    # Benchmark BENCH-01
    bench_res = client.get("/api/v1/benchmarking?project_id=BENCH-01")
    assert bench_res.status_code == 200
    data = bench_res.json()
    assert data["target_project"]["project_code"] == "BENCH-01"
    assert data["cohort_count"] >= 1
    assert data["similar_projects"][0]["project_code"] == "BENCH-02"
    assert data["similar_projects"][0]["similarity_score"] > 0.8

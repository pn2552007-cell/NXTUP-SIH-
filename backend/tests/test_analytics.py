import pytest

def test_analytics_endpoints_zero_data(client):
    # 1. Overview
    res = client.get("/api/analytics/overview")
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["total_trainees"] == 0
    assert data["employment_rate_pct"] == 0.0
    assert data["retention_rate_6m_pct"] is None
    assert data["avg_wage_growth_pct"] is None

    # 2. Employment
    res = client.get("/api/analytics/employment")
    assert res.status_code == 200
    data = res.json()
    assert "status_distribution" in data
    assert data["avg_starting_salary"] is None

    # 3. Retention
    res = client.get("/api/analytics/retention")
    assert res.status_code == 200
    data = res.json()
    assert "checkpoints" in data
    assert data["summary"] == "Insufficient data"

    # 4. Wage Growth
    res = client.get("/api/analytics/wage-growth")
    assert res.status_code == 200
    data = res.json()
    assert data["has_data"] is False
    assert data["avg_growth_pct"] is None

    # 5. Skill Gaps
    res = client.get("/api/analytics/skill-gaps")
    assert res.status_code == 200
    data = res.json()
    assert data["has_data"] is False
    assert data["top_missing_skills"] == []

    # 6. Providers
    res = client.get("/api/analytics/providers")
    assert res.status_code == 200
    assert res.json() == []

    # 7. Courses
    res = client.get("/api/analytics/courses")
    assert res.status_code == 200
    assert res.json() == []

    # 8. Districts
    res = client.get("/api/analytics/districts")
    assert res.status_code == 200
    assert res.json() == []

def test_analytics_endpoints_with_populated_data(client):
    # Populate a trainee and report employment
    tr_res = client.post("/api/auth/register", json={
        "email": "analytictrainee@example.com",
        "password": "Password123!",
        "full_name": "Analytics Trainee",
        "role": "TRAINEE",
        "district": "Pune",
        "state": "Maharashtra"
    })
    tr_token = tr_res.json()["access_token"]
    tr_headers = {"Authorization": f"Bearer {tr_token}"}

    # Grant consent
    client.post("/api/consent", headers=tr_headers, json={
        "consent_status": True,
        "consent_version": "v1.0",
        "purpose": "Analytics verification",
        "consent_text": "I consent."
    })

    # Report employment
    client.post("/api/employment", headers=tr_headers, json={
        "status": "EMPLOYED",
        "employer_name": "Apex IT",
        "job_title": "Software Engineer",
        "joining_date": "2026-02-01",
        "starting_salary": 25000.0,
        "location_city": "Pune"
    })

    # Query overview analytics
    ov_res = client.get("/api/analytics/overview")
    assert ov_res.status_code == 200
    data = ov_res.json()
    assert data["total_trainees"] >= 1
    assert data["employment_rate_pct"] > 0.0

    # Query district analytics
    dist_res = client.get("/api/analytics/districts")
    assert dist_res.status_code == 200
    dist_data = dist_res.json()
    assert len(dist_data) >= 1
    assert any(d["district"] == "Pune" for d in dist_data)

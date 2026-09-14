import pytest

def test_followup_scheduling_and_response(client):
    # Register Trainee
    tr_res = client.post("/api/auth/register", json={
        "email": "followup.trainee@example.com",
        "password": "Password123!",
        "full_name": "Deepak Verma",
        "role": "TRAINEE"
    })
    token = tr_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    assert client.post("/api/consent", headers=headers, json={"consent_status": True}).status_code == 200

    # 1. Schedule followups
    sched_res = client.post("/api/followups/schedule", headers=headers)
    assert sched_res.status_code == 200, sched_res.text
    assert "Successfully scheduled" in sched_res.json()["message"]

    # 2. Get list of scheduled followups
    list_res = client.get("/api/followups", headers=headers)
    assert list_res.status_code == 200
    items = list_res.json()
    assert len(items) == 4  # 30_DAYS, 90_DAYS, 6_MONTHS, 12_MONTHS
    assert items[0]["checkpoint"] == "30_DAYS"
    assert items[0]["status"] == "SCHEDULED"
    followup_id = items[0]["id"]

    # 3. Respond to followup
    resp_res = client.post("/api/followups/respond", headers=headers, json={
        "followup_id": followup_id,
        "employed": True,
        "employer_name": "Global Tech",
        "job_title": "Support Engineer",
        "current_salary": 28000.0,
        "satisfaction_score": 5,
    })
    assert resp_res.status_code == 200, resp_res.text
    updated = resp_res.json()
    assert updated["status"] == "RESPONDED"

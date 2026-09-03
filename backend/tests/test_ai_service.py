import pytest
from app.ai.ai_client import AIClient
from app.ai.ai_service import AIService

def test_ai_service_unconfigured_safe_handling():
    # Client with empty key
    client = AIClient(api_key="")
    assert not client.is_configured()

    service = AIService(client=client)
    res = service.analyze_skill_gap(
        trainee_skills=["Python", "SQL"],
        target_role="Data Engineer"
    )

    # Must return safe structure without crashing
    assert res["available"] is False
    assert "error" in res
    assert res["job_readiness"] >= 0
    assert "strengths" in res
    assert "skill_gaps" in res
    assert res["summary"] != ""

def test_ai_endpoint_safe_response_via_api(client):
    # Register and authenticate a trainee
    reg_res = client.post("/api/auth/register", json={
        "email": "ai.trainee@example.com",
        "password": "Password123!",
        "full_name": "AI Test Trainee",
        "role": "TRAINEE"
    })
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post("/api/ai/skill-gap", headers=headers, json={
        "trainee_skills": ["JavaScript", "React"],
        "target_role": "Frontend Developer"
    })
    assert res.status_code == 200, res.text
    data = res.json()
    assert "skill_gap_score" in data
    assert "target_role" in data
    assert data["target_role"] == "Frontend Developer"

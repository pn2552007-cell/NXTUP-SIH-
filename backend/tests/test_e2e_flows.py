"""
End-to-end verification script for NEXTUP Registration & Admin Flows.
"""
import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_trainee_registration_and_login():
    unique_email = f"trainee_{uuid.uuid4().hex[:8]}@test.nextup.org"
    password = "SecurePassword123!"
    
    # 1. Register Trainee
    reg_resp = client.post("/api/auth/register", json={
        "email": unique_email,
        "password": password,
        "full_name": "Test Trainee User",
        "role": "TRAINEE",
        "phone": "+91 9988776655",
        "state": "Karnataka",
        "district": "Bengaluru Urban"
    })
    assert reg_resp.status_code == 200, f"Register failed: {reg_resp.text}"
    data = reg_resp.json()
    assert "access_token" in data
    assert data["role"] == "TRAINEE"
    assert "nextup_id" in data
    assert data["nextup_id"].startswith("NXT-")

    # 2. Login immediately with registered credentials
    login_resp = client.post("/api/auth/login", json={
        "email": unique_email,
        "password": password
    })
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    token_data = login_resp.json()
    assert "access_token" in token_data
    assert token_data["role"] == "TRAINEE"


def test_provider_registration_and_login():
    unique_email = f"provider_{uuid.uuid4().hex[:8]}@test.nextup.org"
    password = "SecurePassword123!"
    
    # 1. Register Provider
    reg_resp = client.post("/api/auth/register", json={
        "email": unique_email,
        "password": password,
        "full_name": "Dr. Ramesh Sharma",
        "role": "PROVIDER",
        "phone": "+91 9988776654",
        "organization_name": "Apex Skilling Institute",
        "state": "Maharashtra",
        "district": "Pune"
    })
    assert reg_resp.status_code == 200, f"Register failed: {reg_resp.text}"
    data = reg_resp.json()
    assert "access_token" in data
    assert data["role"] in ["PROVIDER", "TRAINING_PROVIDER"]

    # 2. Login
    login_resp = client.post("/api/auth/login", json={
        "email": unique_email,
        "password": password
    })
    assert login_resp.status_code == 200
    token_data = login_resp.json()
    assert token_data["role"] in ["PROVIDER", "TRAINING_PROVIDER"]


def test_employer_registration_and_login():
    unique_email = f"employer_{uuid.uuid4().hex[:8]}@test.nextup.org"
    password = "SecurePassword123!"
    
    # 1. Register Employer
    reg_resp = client.post("/api/auth/register", json={
        "email": unique_email,
        "password": password,
        "full_name": "Kavita Nair",
        "role": "EMPLOYER",
        "phone": "+91 9988776653",
        "organization_name": "TechCore Solutions Ltd",
        "state": "Telangana",
        "district": "Hyderabad"
    })
    assert reg_resp.status_code == 200, f"Register failed: {reg_resp.text}"
    data = reg_resp.json()
    assert "access_token" in data
    assert data["role"] == "EMPLOYER"

    # 2. Login
    login_resp = client.post("/api/auth/login", json={
        "email": unique_email,
        "password": password
    })
    assert login_resp.status_code == 200
    token_data = login_resp.json()
    assert token_data["role"] == "EMPLOYER"


def test_admin_portal_access_and_metrics():
    # 1. Login as Admin
    login_resp = client.post("/api/auth/login", json={
        "email": "admin@nextup.demo",
        "password": "NextUp@Demo2026!"
    })
    assert login_resp.status_code == 200, f"Admin login failed: {login_resp.text}"
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Access Admin Dashboard
    dash_resp = client.get("/api/admin/dashboard", headers=headers)
    assert dash_resp.status_code == 200
    dash_data = dash_resp.json()
    assert dash_data["total_trainees"] >= 51
    assert "macro_employment_rate" in dash_data
    assert "provider_rankings" in dash_data
    assert len(dash_data["provider_rankings"]) > 0
    assert "domains_breakdown" in dash_data
    assert "districts_data" in dash_data

    # 3. Access Admin Trainees list
    trainees_resp = client.get("/api/admin/trainees", headers=headers)
    assert trainees_resp.status_code == 200
    trainees_data = trainees_resp.json()
    assert trainees_data["total"] >= 51
    assert len(trainees_data["items"]) > 0
    assert "nextup_id" in trainees_data["items"][0]

    # 4. Access Admin Users list
    users_resp = client.get("/api/admin/users", headers=headers)
    assert users_resp.status_code == 200
    users_data = users_resp.json()
    assert users_data["total"] >= 50

    # 5. Access Admin Training batches
    training_resp = client.get("/api/admin/training", headers=headers)
    assert training_resp.status_code == 200

    # 6. Access Admin Certificates
    certs_resp = client.get("/api/admin/certificates", headers=headers)
    assert certs_resp.status_code == 200

    # 7. Access Admin Employment
    emp_resp = client.get("/api/admin/employment", headers=headers)
    assert emp_resp.status_code == 200

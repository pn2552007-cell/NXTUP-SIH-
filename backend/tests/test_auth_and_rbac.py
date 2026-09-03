import pytest

def test_user_registration_and_login(client):
    # 1. Register Trainee
    reg_payload = {
        "email": "priya.nair@example.com",
        "password": "SecurePassword123!",
        "full_name": "Priya Nair",
        "role": "TRAINEE",
        "phone": "+919876543210",
        "state": "Maharashtra",
        "district": "Pune"
    }
    reg_res = client.post("/api/auth/register", json=reg_payload)
    assert reg_res.status_code == 200, reg_res.text
    data = reg_res.json()
    assert data["email"] == "priya.nair@example.com"
    assert data["role"] == "TRAINEE"
    assert "access_token" in data

    # 2. Login with registered credentials
    login_res = client.post("/api/auth/login", json={
        "email": "priya.nair@example.com",
        "password": "SecurePassword123!"
    })
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    assert token is not None

    # 3. Test /auth/me
    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["full_name"] == "Priya Nair"
    assert me_data["role"] == "TRAINEE"

def test_login_invalid_password_rejected(client):
    res = client.post("/api/auth/login", json={
        "email": "priya.nair@example.com",
        "password": "WrongPassword999!"
    })
    assert res.status_code == 401

def test_rbac_authorization(client):
    # Register an employer
    client.post("/api/auth/register", json={
        "email": "hr@acmecorp.com",
        "password": "SecurePassword123!",
        "full_name": "Acme HR Manager",
        "role": "EMPLOYER",
        "organization_name": "Acme Corp"
    })
    login_res = client.post("/api/auth/login", json={
        "email": "hr@acmecorp.com",
        "password": "SecurePassword123!"
    })
    emp_token = login_res.json()["access_token"]
    emp_headers = {"Authorization": f"Bearer {emp_token}"}

    # Employer should be allowed to access employer dashboard
    emp_dash_res = client.get("/api/employer/dashboard", headers=emp_headers)
    assert emp_dash_res.status_code == 200

    # Employer should NOT be allowed to access trainee profile
    trainee_prof_res = client.get("/api/trainee/profile", headers=emp_headers)
    assert trainee_prof_res.status_code == 403

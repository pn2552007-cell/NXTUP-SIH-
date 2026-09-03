import pytest

def test_employment_reporting_and_employer_verification(client):
    # 1. Register Trainee and Provider
    tr_res = client.post("/api/auth/register", json={
        "email": "placed.trainee@example.com",
        "password": "Password123!",
        "full_name": "Karan Mehra",
        "role": "TRAINEE"
    })
    tr_token = tr_res.json()["access_token"]
    tr_headers = {"Authorization": f"Bearer {tr_token}"}

    # Grant consent
    client.post("/api/consent", headers=tr_headers, json={
        "consent_status": True,
        "consent_version": "v1.0",
        "purpose": "Employment verification",
        "consent_text": "I consent."
    })

    # 2. Register Employer
    emp_res = client.post("/api/auth/register", json={
        "email": "hr@technocraft.com",
        "password": "Password123!",
        "full_name": "Technocraft HR",
        "role": "EMPLOYER",
        "organization_name": "Technocraft Solutions"
    })
    emp_token = emp_res.json()["access_token"]
    emp_headers = {"Authorization": f"Bearer {emp_token}"}

    # 3. Trainee reports employment
    rep_res = client.post("/api/employment", headers=tr_headers, json={
        "status": "EMPLOYED",
        "employer_name": "Technocraft Solutions",
        "job_title": "Backend Developer",
        "joining_date": "2026-03-01",
        "starting_salary": 32000.0,
        "location_city": "Pune"
    })
    assert rep_res.status_code == 200, rep_res.text
    emp_record = rep_res.json()
    assert emp_record["employer_name"] == "Technocraft Solutions"
    assert emp_record["verification_status"] == "PENDING"
    emp_record_id = emp_record["id"]

    # 4. Employer sees pending verification on dashboard
    emp_dash_res = client.get("/api/employer/dashboard", headers=emp_headers)
    assert emp_dash_res.status_code == 200
    pending_list = emp_dash_res.json()["pending_verifications"]
    assert len(pending_list) >= 1
    assert any(p["id"] == emp_record_id for p in pending_list)

    # 5. Employer verifies record with matching details
    verify_res = client.post("/api/employer/verify", headers=emp_headers, json={
        "employment_record_id": emp_record_id,
        "status": "VERIFIED",
        "is_verified": True,
        "verified_job_title": "Backend Developer",
        "verified_joining_date": "2026-03-01",
        "verified_salary": 32000.0,
        "verification_notes": "Employee confirmed on payroll."
    })
    assert verify_res.status_code == 200, verify_res.text
    verify_data = verify_res.json()
    assert verify_data["status"] == "VERIFIED"
    assert verify_data["confidence_score"] >= 0.60, "Derived confidence based on match criteria"

    # 6. Trainee verifies updated wage growth
    wage_res = client.get("/api/trainee/wage-growth", headers=tr_headers)
    assert wage_res.status_code == 200
    wage_data = wage_res.json()
    assert wage_data["has_history"] is True
    assert wage_data["starting_salary"] == 32000.0
    assert wage_data["current_salary"] == 32000.0
    assert wage_data["overall_growth_pct"] == 0.0

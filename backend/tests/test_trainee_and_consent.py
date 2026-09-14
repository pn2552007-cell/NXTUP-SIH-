import re
import pytest

def test_skillpulse_id_format_and_uniqueness(client):
    # Register 2 trainees
    t1_res = client.post("/api/auth/register", json={
        "email": "trainee1@example.com",
        "password": "Password123!",
        "full_name": "Trainee One",
        "role": "TRAINEE"
    })
    assert t1_res.status_code == 200
    id1 = t1_res.json()["skillpulse_id"]

    t2_res = client.post("/api/auth/register", json={
        "email": "trainee2@example.com",
        "password": "Password123!",
        "full_name": "Trainee Two",
        "role": "TRAINEE"
    })
    assert t2_res.status_code == 200
    id2 = t2_res.json()["skillpulse_id"]

    # Verify NXT-YYYY-XXXXXX format (or legacy SP-XXXXXXXX)
    pattern = r"^(NXT-\d{4}-[A-Z0-9]{6}|SP-[A-Z0-9]{8})$"
    assert re.match(pattern, id1), f"ID '{id1}' does not match NEXTUP pattern NXT-YYYY-XXXXXX"
    assert re.match(pattern, id2), f"ID '{id2}' does not match NEXTUP pattern NXT-YYYY-XXXXXX"
    assert id1 != id2, "Generated IDs must be unique and non-sequential"

def test_consent_granting_and_revocation(client):
    # Register trainee
    reg_res = client.post("/api/auth/register", json={
        "email": "consent.trainee@example.com",
        "password": "Password123!",
        "full_name": "Consent Trainee",
        "role": "TRAINEE"
    })
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Check initial consent status
    st_res = client.get("/api/consent/status", headers=headers)
    assert st_res.status_code == 200
    assert st_res.json()["consent_given"] is False

    # 2. Grant consent with purpose
    grant_res = client.post("/api/consent", headers=headers, json={
        "consent_status": True,
        "consent_version": "v1.0",
        "purpose": "Longitudinal outcome tracking",
        "consent_text": "I grant consent for longitudinal tracking."
    })
    assert grant_res.json()["consent_status"] is True

    # Check updated status
    st_res2 = client.get("/api/consent/status", headers=headers)
    assert st_res2.json()["consent_given"] is True

    # 3. Revoke consent
    revoke_res = client.post("/api/consent/revoke", headers=headers, json={
        "reason": "Trainee opted out."
    })
    assert revoke_res.status_code == 200
    assert revoke_res.json()["status"] == "revoked"

    st_res3 = client.get("/api/consent/status", headers=headers)
    assert st_res3.json()["consent_given"] is False

    # 4. Check audit trail
    audit_res = client.get("/api/consent/audit-trail", headers=headers)
    assert audit_res.status_code == 200
    trail = audit_res.json()
    assert len(trail) >= 1
    assert trail[0]["status"] == "REVOKED"

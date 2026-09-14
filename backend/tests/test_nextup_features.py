"""
Tests for NEXTUP Features — SIH26135 | Team Lumora
===================================================
Tests for:
1. NEXTUP persistent ID generation (NXT-YYYY-XXXXXX)
2. ML Placement Risk Prediction endpoint (/api/ml/predict-risk)
3. ML Model Info endpoint (/api/ml/model-info)
4. ML Recommendation Service (/api/ml/recommend-intervention)
5. Jobs & Job Requirements API (/api/jobs)
6. Retrain Status API (/api/ml/retrain-status)
"""
import pytest
from app.utils.id_generator import generate_nextup_id, generate_skillpulse_id
from app.auth.jwt_handler import create_access_token, get_password_hash
from app.models.models import (
    User, Trainee, Provider, Course, TrainingRecord, EmploymentRecord,
    Outcome, Job, JobRequirement, Intervention,
)


@pytest.fixture
def test_admin_token(db_session):
    admin_user = User(
        email="test_nextup_admin@nextup.demo",
        hashed_password=get_password_hash("NextUp@Demo2026!"),
        role="ADMIN",
        full_name="NEXTUP Admin Test",
        is_active=True,
    )
    db_session.add(admin_user)
    db_session.commit()
    db_session.refresh(admin_user)

    token = create_access_token(data={"sub": str(admin_user.id), "role": "ADMIN"})
    return token


def test_nextup_id_format(db_session):
    """Verify NEXTUP ID follows standard NXT-YYYY-XXXXXX format."""
    nid = generate_nextup_id(db_session)
    assert nid.startswith("NXT-")
    parts = nid.split("-")
    assert len(parts) == 3
    assert len(parts[1]) == 4  # Year e.g. 2026
    assert len(parts[2]) == 6  # 6 alphanumeric characters
    assert parts[2].isalnum()


def test_backward_compat_skillpulse_id(db_session):
    """Verify legacy generator redirects to NXT format."""
    sid = generate_skillpulse_id(db_session)
    assert sid.startswith("NXT-")


def test_get_model_info(client, test_admin_token):
    """Test retrieving ML model architecture info and disclaimer."""
    headers = {"Authorization": f"Bearer {test_admin_token}"}
    resp = client.get("/api/ml/model-info", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "model_name" in data or "model_type" in data
    assert "features" in data
    assert "disclaimer" in data
    assert "synthetic" in data["disclaimer"].lower() or "prototype" in data["disclaimer"].lower() or "demo" in data["disclaimer"].lower()


def test_predict_risk_synthetic(client, test_admin_token):
    """Test running ML risk prediction with explicit feature inputs."""
    headers = {"Authorization": f"Bearer {test_admin_token}"}
    payload = {
        "attendance_pct": 88.0,
        "assessment_avg_score": 82.0,
        "certification_status": 1,
        "skill_gap_score": 25.0,
        "verified_skill_count": 5,
        "course_domain": "Information Technology",
        "state": "Maharashtra",
    }
    resp = client.post("/api/ml/predict-risk", json=payload, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["available"] is False
    assert data["status"] == "PLANNED"
    assert data["risk_score"] is None
    assert data["prob_placed"] is None
    assert isinstance(data["contributing_factors"], list)
    assert "disclaimer" in data


def test_recommend_intervention(client, test_admin_token):
    """Test generating a targeted remedial intervention."""
    headers = {"Authorization": f"Bearer {test_admin_token}"}
    payload = {
        "risk_level": "HIGH",
        "risk_score": 78.5,
        "missing_skills": ["Docker", "Kubernetes"],
        "target_job": "DevOps Engineer",
    }
    resp = client.post("/api/ml/recommend-intervention", json=payload, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "title" in data
    assert "recommended_actions" in data
    assert len(data["recommended_actions"]) > 0


def test_retrain_status(client, test_admin_token):
    """Test checking model retraining pipeline status."""
    headers = {"Authorization": f"Bearer {test_admin_token}"}
    resp = client.get("/api/ml/retrain-status", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "status" in data
    assert "retraining_ready" in data
    assert "min_required" in data
    assert data["status"] == "PLANNED"
    assert data["retraining_ready"] is False
    assert "accuracy" not in data["message"].lower()


def test_admin_dashboard_filters_and_trust_split(client, test_admin_token, db_session):
    """Admin dashboard metrics come from scoped current outcomes, not defaults."""
    provider_a = Provider(
        organization_name="NXTUP Pune Skills",
        code="TST-PUNE",
        email="pune-provider@example.com",
        state="Maharashtra",
        district="Pune",
    )
    provider_b = Provider(
        organization_name="NXTUP Jaipur Skills",
        code="TST-JAIPUR",
        email="jaipur-provider@example.com",
        state="Rajasthan",
        district="Jaipur",
    )
    db_session.add_all([provider_a, provider_b])
    db_session.commit()
    db_session.refresh(provider_a)
    db_session.refresh(provider_b)

    course_a = Course(provider_id=provider_a.id, course_name="Backend Pilot", domain="IT")
    course_b = Course(provider_id=provider_b.id, course_name="Retail Pilot", domain="Retail")
    db_session.add_all([course_a, course_b])
    db_session.commit()
    db_session.refresh(course_a)
    db_session.refresh(course_b)

    trainee_a = Trainee(
        skillpulse_id="NXT-2026-TSTA01",
        nextup_id="NXT-2026-TSTA01",
        full_name="Verified Pune Trainee",
        email="verified-pune@example.com",
        state="Maharashtra",
        district="Pune",
        consent_given=True,
    )
    trainee_b = Trainee(
        skillpulse_id="NXT-2026-TSTB01",
        nextup_id="NXT-2026-TSTB01",
        full_name="Pending Jaipur Trainee",
        email="pending-jaipur@example.com",
        state="Rajasthan",
        district="Jaipur",
        consent_given=True,
    )
    db_session.add_all([trainee_a, trainee_b])
    db_session.commit()
    db_session.refresh(trainee_a)
    db_session.refresh(trainee_b)

    db_session.add_all([
        TrainingRecord(
            trainee_id=trainee_a.id,
            course_id=course_a.id,
            provider_id=provider_a.id,
            cohort_id="PILOT-A",
            completion_status="COMPLETED",
            start_date="2026-01-01",
            end_date="2026-03-01",
        ),
        TrainingRecord(
            trainee_id=trainee_b.id,
            course_id=course_b.id,
            provider_id=provider_b.id,
            cohort_id="PILOT-B",
            completion_status="COMPLETED",
            start_date="2026-01-01",
            end_date="2026-03-01",
        ),
    ])
    db_session.flush()

    emp_a = EmploymentRecord(
        trainee_id=trainee_a.id,
        employer_name="Verified Employer",
        job_title="Associate Developer",
        status="EMPLOYED",
        verification_status="VERIFIED",
        starting_salary=25000,
        current_salary=30000,
    )
    emp_b = EmploymentRecord(
        trainee_id=trainee_b.id,
        employer_name="Pending Employer",
        job_title="Retail Associate",
        status="EMPLOYED",
        verification_status="PENDING",
        starting_salary=18000,
        current_salary=18000,
    )
    db_session.add_all([emp_a, emp_b])
    db_session.commit()
    db_session.refresh(emp_a)

    db_session.add(Outcome(
        trainee_id=trainee_a.id,
        employment_record_id=emp_a.id,
        placement_status=1,
        is_verified=True,
        verification_source="EMPLOYER_PORTAL",
    ))
    db_session.commit()

    headers = {"Authorization": f"Bearer {test_admin_token}"}
    all_res = client.get("/api/admin/dashboard", headers=headers)
    assert all_res.status_code == 200, all_res.text
    all_data = all_res.json()
    assert all_data["total_trainees"] == 2
    assert all_data["employed_trainees"] == 2
    assert all_data["verified_employment"] == 1
    assert all_data["self_reported_employment"] == 1
    assert all_data["ai_status"]["placement_risk_model"]["status"] == "PLANNED"

    scoped_res = client.get(f"/api/admin/dashboard?provider_id={provider_a.id}", headers=headers)
    assert scoped_res.status_code == 200, scoped_res.text
    scoped = scoped_res.json()
    assert scoped["total_trainees"] == 1
    assert scoped["verified_employment"] == 1
    assert scoped["self_reported_employment"] == 0
    assert scoped["active_filters"]["provider_id"] == provider_a.id


def test_jobs_list(client, test_admin_token, db_session):
    """Test querying target jobs catalogue."""
    # Ensure at least one test job exists
    existing = db_session.query(Job).filter(Job.title == "Junior Python Engineer").first()
    if not existing:
        j = Job(
            title="Junior Python Engineer",
            domain="Information Technology",
            description="Test engineering role",
            salary_range_min=25000.0,
            salary_range_max=45000.0,
            demand_level="HIGH",
            is_active=True,
        )
        db_session.add(j)
        db_session.commit()
        db_session.refresh(j)

        req = JobRequirement(
            job_id=j.id,
            skill_name="Python",
            min_proficiency="INTERMEDIATE",
            is_mandatory=True,
        )
        db_session.add(req)
        db_session.commit()

    headers = {"Authorization": f"Bearer {test_admin_token}"}
    resp = client.get("/api/jobs", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(job["title"] == "Junior Python Engineer" for job in data)

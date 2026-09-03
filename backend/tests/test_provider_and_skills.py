import pytest
from app.utils.skill_normalizer import normalize_skill_name

def test_skill_normalizer_canonical_casing():
    assert normalize_skill_name("python") == "Python"
    assert normalize_skill_name("PYTHON") == "Python"
    assert normalize_skill_name("javascript") == "JavaScript"
    assert normalize_skill_name("react.js") == "React"
    assert normalize_skill_name("docker") == "Docker"
    assert normalize_skill_name("  kubernetes  ") == "Kubernetes"

def test_course_and_batch_creation(client):
    # Register Provider
    prv_res = client.post("/api/auth/register", json={
        "email": "director@aptechskills.com",
        "password": "Password123!",
        "full_name": "Dr. Ramesh Gupta",
        "role": "PROVIDER",
        "organization_name": "Aptech Skills Institute"
    })
    prv_token = prv_res.json()["access_token"]
    prv_headers = {"Authorization": f"Bearer {prv_token}"}

    # 1. Create Course
    course_res = client.post("/api/providers/courses", headers=prv_headers, json={
        "course_name": "Full Stack Cloud Development",
        "domain": "IT",
        "duration_weeks": 16,
        "required_skills": ["python", "docker", "fastapi", "react.js"],
        "description": "Comprehensive full stack cloud curriculum"
    })
    assert course_res.status_code == 200, course_res.text
    course = course_res.json()
    assert course["course_name"] == "Full Stack Cloud Development"
    course_id = course["id"]

    # Verify skills normalized
    assert "Python" in course["required_skills"]
    assert "Docker" in course["required_skills"]

    # 2. Create Batch
    batch_res = client.post("/api/providers/batches", headers=prv_headers, json={
        "batch_name": "BATCH-2026-CLOUD-01",
        "course_id": course_id,
        "start_date": "2026-01-15",
        "end_date": "2026-05-15",
        "trainer_name": "Vikas Patil"
    })
    assert batch_res.status_code == 200, batch_res.text
    batch = batch_res.json()
    assert batch["batch_name"] == "BATCH-2026-CLOUD-01"
    batch_id = batch["id"]

    # 3. Enroll Trainee
    # First create a trainee
    tr_res = client.post("/api/auth/register", json={
        "email": "student1@aptechskills.com",
        "password": "Password123!",
        "full_name": "Sneha Joshi",
        "role": "TRAINEE"
    })
    trainee_id = tr_res.json()["user_id"]

    enroll_res = client.post("/api/providers/enroll", headers=prv_headers, json={
        "trainee_id": trainee_id,
        "course_id": course_id,
        "batch_id": batch_id
    })
    assert enroll_res.status_code == 200, enroll_res.text
    enrollment = enroll_res.json()
    assert enrollment["status"] == "ENROLLED"
    assert enrollment["course_id"] == course_id

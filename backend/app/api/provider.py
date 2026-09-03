from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Response
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.models import (
    User, Provider, Course, TrainingBatch, Enrollment, TrainingRecord, Assessment,
    Certification, Trainee, EmploymentRecord, SkillGapAnalysis, Followup
)
from app.schemas.schemas import (
    CourseCreate, CourseResponse, TrainingBatchCreate, TrainingBatchResponse,
    EnrollmentCreate, EnrollmentResponse, AssessmentCreate, AssessmentResponse,
    CertificationCreate, CertificationResponse, CsvImportResponse
)
from app.auth.jwt_handler import get_current_user, require_role
from app.services.csv_import_service import CsvImportService
from app.utils.skill_normalizer import normalize_skill_list
from app.utils.audit import log_audit_event

router = APIRouter(prefix="/providers", tags=["Training Provider Operations"])

@router.get("/dashboard")
def get_provider_dashboard(
    cohort: Optional[str] = None,
    course_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Find provider linked to current user or if admin allow query
    provider = db.query(Provider).filter(Provider.user_id == current_user.id).first()
    if not provider and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Provider profile not found for this user.")

    provider_id = provider.id if provider else None

    # Base query for training records
    t_query = db.query(TrainingRecord)
    if provider_id:
        t_query = t_query.filter(TrainingRecord.provider_id == provider_id)
    if cohort and cohort != "ALL":
        t_query = t_query.filter(TrainingRecord.cohort_id == cohort)
    if course_id:
        t_query = t_query.filter(TrainingRecord.course_id == course_id)

    training_records = t_query.all()
    total_trainees = len(training_records)
    trainee_ids = [r.trainee_id for r in training_records]

    # Dynamically calculated from actual database
    completed_count = sum(1 for r in training_records if r.completion_status == "COMPLETED")
    completion_rate = round((completed_count / max(total_trainees, 1)) * 100.0, 1) if total_trainees > 0 else 0.0

    cert_count = db.query(Certification).filter(Certification.trainee_id.in_(trainee_ids)).count() if trainee_ids else 0
    cert_rate = round((cert_count / max(total_trainees, 1)) * 100.0, 1) if total_trainees > 0 else 0.0

    emp_records = db.query(EmploymentRecord).filter(
        EmploymentRecord.trainee_id.in_(trainee_ids),
        EmploymentRecord.status == "EMPLOYED"
    ).all() if trainee_ids else []
    employed_count = len(emp_records)
    emp_rate = round((employed_count / max(total_trainees, 1)) * 100.0, 1) if total_trainees > 0 else 0.0
    placement_conversion = round((employed_count / max(cert_count, 1)) * 100.0, 1) if cert_count > 0 else 0.0

    # Salaries
    salaries = [e.starting_salary for e in emp_records if e.starting_salary is not None]
    current_salaries = [e.current_salary for e in emp_records if e.current_salary is not None]
    avg_start_sal = round(sum(salaries) / len(salaries), 2) if salaries else None
    avg_curr_sal = round(sum(current_salaries) / len(current_salaries), 2) if current_salaries else None

    # Time to employment
    time_to_emp_list = []
    for r in training_records:
        if r.end_date:
            emp = next((e for e in emp_records if e.trainee_id == r.trainee_id and e.joining_date), None)
            if emp:
                try:
                    t_end = datetime.strptime(r.end_date, "%Y-%m-%d")
                    e_join = datetime.strptime(emp.joining_date, "%Y-%m-%d")
                    days = (e_join - t_end).days
                    if days >= 0:
                        time_to_emp_list.append(days)
                except Exception:
                    pass
    avg_time_to_emp_days = round(sum(time_to_emp_list) / len(time_to_emp_list), 1) if time_to_emp_list else None

    # Skill gaps
    gap_records = db.query(SkillGapAnalysis).filter(SkillGapAnalysis.trainee_id.in_(trainee_ids)).all() if trainee_ids else []
    avg_gap = round(sum(g.skill_gap_score for g in gap_records) / len(gap_records), 1) if gap_records else None

    # Follow-ups
    fup_total = db.query(Followup).filter(Followup.trainee_id.in_(trainee_ids)).count() if trainee_ids else 0
    fup_responded = db.query(Followup).filter(Followup.trainee_id.in_(trainee_ids), Followup.status == "RESPONDED").count() if trainee_ids else 0
    followup_completion_rate = round((fup_responded / max(fup_total, 1)) * 100.0, 1) if fup_total > 0 else 0.0

    # Course breakdown
    courses_query = db.query(Course)
    if provider_id:
        courses_query = courses_query.filter(Course.provider_id == provider_id)
    courses = courses_query.all()

    course_items = []
    for c in courses:
        c_recs = [r for r in training_records if r.course_id == c.id]
        c_total = len(c_recs)
        c_trainee_ids = [r.trainee_id for r in c_recs]
        c_certs = db.query(Certification).filter(Certification.trainee_id.in_(c_trainee_ids)).count() if c_trainee_ids else 0
        c_emp = db.query(EmploymentRecord).filter(
            EmploymentRecord.trainee_id.in_(c_trainee_ids),
            EmploymentRecord.status == "EMPLOYED"
        ).all() if c_trainee_ids else []
        c_sal = [e.current_salary for e in c_emp if e.current_salary is not None]

        course_items.append({
            "course_id": c.id,
            "course_name": c.course_name,
            "domain": c.domain,
            "total_enrolled": c_total,
            "certified_count": c_certs,
            "employed_count": len(c_emp),
            "certification_rate": round((c_certs / max(c_total, 1)) * 100.0, 1) if c_total > 0 else 0.0,
            "employment_rate": round((len(c_emp) / max(c_total, 1)) * 100.0, 1) if c_total > 0 else 0.0,
            "avg_salary": round(sum(c_sal) / len(c_sal), 2) if c_sal else None
        })

    return {
        "provider_name": provider.organization_name if provider else "All Providers (Admin View)",
        "total_trainees": total_trainees,
        "completion_rate": completion_rate,
        "certification_rate": cert_rate,
        "employment_rate": emp_rate,
        "placement_conversion": placement_conversion,
        "avg_starting_salary": avg_start_sal,
        "avg_current_salary": avg_curr_sal,
        "avg_time_to_employment_days": avg_time_to_emp_days,
        "avg_skill_gap": avg_gap,
        "followup_completion_rate": followup_completion_rate,
        "courses_performance": course_items,
        "active_filters": {"cohort": cohort or "ALL", "course_id": course_id}
    }

@router.post("/courses", response_model=CourseResponse)
def create_course(
    course_in: CourseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    provider = db.query(Provider).filter(Provider.user_id == current_user.id).first()
    if not provider and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Only training providers can create courses.")

    provider_id = provider.id if provider else db.query(Provider).first().id

    norm_skills = normalize_skill_list(course_in.required_skills or [])

    course = Course(
        provider_id=provider_id,
        course_name=course_in.course_name,
        domain=course_in.domain,
        duration_weeks=course_in.duration_weeks,
        description=course_in.description,
        target_roles=course_in.target_roles or [],
        required_skills=norm_skills
    )
    db.add(course)
    db.commit()
    db.refresh(course)

    log_audit_event(
        db=db,
        action="COURSE_CREATED",
        entity_type="COURSE",
        entity_id=str(course.id),
        user_id=current_user.id,
        details={"course_name": course.course_name, "provider_id": provider_id}
    )

    return course

@router.get("/courses", response_model=List[CourseResponse])
def list_courses(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    provider = db.query(Provider).filter(Provider.user_id == current_user.id).first()
    query = db.query(Course)
    if provider and current_user.role != "ADMIN":
        query = query.filter(Course.provider_id == provider.id)
    return query.all()

@router.post("/batches", response_model=TrainingBatchResponse)
def create_batch(
    batch_in: TrainingBatchCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    provider = db.query(Provider).filter(Provider.user_id == current_user.id).first()
    if not provider and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Only training providers can create batches.")

    provider_id = provider.id if provider else 1
    batch_code = f"BATCH-{provider_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

    batch = TrainingBatch(
        batch_code=batch_code,
        batch_name=batch_in.batch_name,
        course_id=batch_in.course_id,
        provider_id=provider_id,
        trainer_name=batch_in.trainer_name,
        start_date=batch_in.start_date,
        end_date=batch_in.end_date,
        max_capacity=batch_in.max_capacity
    )
    db.add(batch)
    db.commit()
    db.refresh(batch)

    log_audit_event(
        db=db,
        action="BATCH_CREATED",
        entity_type="TRAINING_BATCH",
        entity_id=str(batch.id),
        user_id=current_user.id,
        details={"batch_code": batch.batch_code}
    )

    return batch

@router.post("/enroll", response_model=EnrollmentResponse)
def enroll_trainee(
    enroll_in: EnrollmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    provider = db.query(Provider).filter(Provider.user_id == current_user.id).first()
    if not provider and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Only training providers or admins can enroll trainees.")

    provider_id = provider.id if provider else 1

    trainee = db.query(Trainee).filter((Trainee.id == enroll_in.trainee_id) | (Trainee.user_id == enroll_in.trainee_id)).first()
    if not trainee:
        raise HTTPException(status_code=404, detail="Trainee not found.")
    resolved_trainee_id = trainee.id

    # Create Enrollment
    enrollment = Enrollment(
        trainee_id=resolved_trainee_id,
        course_id=enroll_in.course_id,
        batch_id=enroll_in.batch_id,
        status="ENROLLED",
        attendance_pct=100.0
    )
    db.add(enrollment)

    # Also link TrainingRecord
    record = TrainingRecord(
        trainee_id=resolved_trainee_id,
        course_id=enroll_in.course_id,
        provider_id=provider_id,
        batch_id=enroll_in.batch_id,
        completion_status="IN_PROGRESS",
        attendance_pct=100.0,
        start_date=datetime.utcnow().strftime("%Y-%m-%d")
    )
    db.add(record)
    db.commit()
    db.refresh(enrollment)

    log_audit_event(
        db=db,
        action="TRAINEE_ENROLLED",
        entity_type="ENROLLMENT",
        entity_id=str(enrollment.id),
        user_id=current_user.id,
        details={"trainee_id": enroll_in.trainee_id, "course_id": enroll_in.course_id}
    )

    return enrollment

@router.post("/assessments", response_model=AssessmentResponse)
def record_assessment(
    assessment_in: AssessmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    pct = round((assessment_in.score / max(assessment_in.max_score, 1.0)) * 100.0, 2)
    assessment = Assessment(
        trainee_id=assessment_in.trainee_id,
        assessment_name=assessment_in.assessment_name,
        skill_name=assessment_in.skill_name,
        assessment_type=assessment_in.assessment_type or "PRACTICAL",
        score=assessment_in.score,
        max_score=assessment_in.max_score,
        pass_status=assessment_in.pass_status,
        date_taken=assessment_in.date_taken or datetime.utcnow().strftime("%Y-%m-%d")
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)

    log_audit_event(
        db=db,
        action="ASSESSMENT_RECORDED",
        entity_type="ASSESSMENT",
        entity_id=str(assessment.id),
        user_id=current_user.id,
        details={"trainee_id": assessment.trainee_id, "score": assessment.score, "pct": pct}
    )

    return AssessmentResponse(
        id=assessment.id,
        trainee_id=assessment.trainee_id,
        assessment_name=assessment.assessment_name,
        skill_name=assessment.skill_name,
        score=assessment.score,
        max_score=assessment.max_score,
        percentage=pct,
        pass_status=assessment.pass_status,
        date_taken=assessment.date_taken
    )

@router.post("/certifications", response_model=CertificationResponse)
def issue_certification(
    cert_in: CertificationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    cert_number = f"CERT-{cert_in.course_id}-{cert_in.trainee_id}-{datetime.utcnow().strftime('%Y%m%d%H%M')}"
    cert = Certification(
        trainee_id=cert_in.trainee_id,
        course_id=cert_in.course_id,
        certificate_number=cert_number,
        issuing_organization=cert_in.issuing_organization or "SkillPulse Verified Provider",
        issue_date=cert_in.issue_date or datetime.utcnow().strftime("%Y-%m-%d"),
        expiry_date=cert_in.expiry_date,
        certificate_url=cert_in.certificate_url,
        related_skills=cert_in.related_skills or [],
        status="ISSUED"
    )
    db.add(cert)
    db.commit()
    db.refresh(cert)

    log_audit_event(
        db=db,
        action="CERTIFICATION_ISSUED",
        entity_type="CERTIFICATION",
        entity_id=str(cert.id),
        user_id=current_user.id,
        details={"trainee_id": cert.trainee_id, "cert_number": cert_number}
    )

    return cert

@router.get("/trainees")
def list_provider_trainees(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    provider = db.query(Provider).filter(Provider.user_id == current_user.id).first()
    if not provider and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Provider profile not found.")

    provider_id = provider.id if provider else None
    query = db.query(TrainingRecord)
    if provider_id:
        query = query.filter(TrainingRecord.provider_id == provider_id)

    records = query.all()
    results = []
    for r in records:
        t = r.trainee
        if not t:
            continue
        emp = db.query(EmploymentRecord).filter(EmploymentRecord.trainee_id == t.id).order_by(EmploymentRecord.created_at.desc()).first()
        results.append({
            "trainee_id": t.id,
            "skillpulse_id": t.skillpulse_id,
            "full_name": t.full_name,
            "email": t.email,
            "phone": t.phone,
            "course_name": r.course.course_name if r.course else None,
            "completion_status": r.completion_status,
            "attendance_pct": r.attendance_pct,
            "employment_status": emp.status if emp else "NOT_REPORTED",
            "employer_name": emp.employer_name if emp else None,
            "verification_status": emp.verification_status if emp else None
        })
    return results

@router.post("/import-trainees", response_model=CsvImportResponse)
async def import_trainees_csv(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    provider = db.query(Provider).filter(Provider.user_id == current_user.id).first()
    if not provider and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Only training providers can import trainee rosters.")

    provider_id = provider.id if provider else 1
    content = await file.read()
    import_result = CsvImportService.process_trainee_roster(db=db, content=content, provider_id=provider_id)
    return import_result

@router.get("/sample-csv")
def download_sample_csv():
    csv_content = (
        "full_name,email,phone,gender,education,district,state,course_name,domain,start_date,end_date\n"
        "Aarav Sharma,aarav.sharma@example.com,9876543210,Male,B.Tech,Pune,Maharashtra,Full Stack Web Development,IT,2025-10-01,2026-01-15\n"
    )
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=skillpulse_sample_roster.csv"}
    )

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import (
    User, Employer, EmploymentRecord, EmployerVerification,
    Trainee, TrainingRecord, Course, TraineeSkill, Assessment, WageHistory
)
from app.schemas.schemas import EmployerVerificationRequest
from app.auth.jwt_handler import get_current_user
from app.utils.audit import log_audit_event

router = APIRouter(prefix="/employer", tags=["Employer Verification & Talent"])

def calculate_verification_confidence(
    status: str,
    reported_salary: Optional[float],
    verified_salary: Optional[float],
    reported_date: Optional[str],
    verified_date: Optional[str],
    employer_is_verified: bool = True
) -> float:
    """
    Computes confidence score derived from actual deterministic verification logic.
    """
    if status == "REJECTED":
        return 0.0

    score = 0.50  # Baseline self-reported confidence

    if employer_is_verified:
        score += 0.35  # Authenticated employer verified the employment

    # Consistency checks
    if reported_salary and verified_salary:
        diff_pct = abs(reported_salary - verified_salary) / max(reported_salary, 1.0)
        if diff_pct <= 0.10:
            score += 0.08  # Salary matches within 10% tolerance

    if reported_date and verified_date and reported_date == verified_date:
        score += 0.07  # Exact joining date match

    return min(round(score, 2), 1.0)

@router.get("/dashboard")
def get_employer_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    employer = db.query(Employer).filter(Employer.user_id == current_user.id).first()
    if not employer and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Employer profile not found.")

    emp_id = employer.id if employer else None
    company_name = employer.company_name if employer else "All Employers (Admin View)"

    query = db.query(EmploymentRecord)
    if emp_id:
        # Match by employer_id or company name
        query = query.filter(
            (EmploymentRecord.employer_id == emp_id) |
            (EmploymentRecord.employer_name.ilike(company_name))
        )

    pending_records = query.filter(EmploymentRecord.verification_status == "PENDING").all()
    verified_records = query.filter(EmploymentRecord.verification_status == "VERIFIED").all()

    def format_item(rec: EmploymentRecord):
        tr = rec.trainee
        t_rec = db.query(TrainingRecord).filter(TrainingRecord.trainee_id == tr.id).first() if tr else None
        return {
            "id": rec.id,
            "employment_record_id": rec.id,
            "trainee_id": tr.id if tr else None,
            "trainee_name": tr.full_name if tr and tr.consent_given else "Candidate Profile",
            "skillpulse_id": tr.skillpulse_id if tr else None,
            "course_name": t_rec.course.course_name if t_rec and t_rec.course else None,
            "reported_job": rec.job_title,
            "reported_joining_date": rec.joining_date,
            "reported_salary": rec.starting_salary,
            "reported_location": f"{rec.location_city or ''}, {rec.location_state or ''}".strip(", "),
            "verification_status": rec.verification_status,
            "confidence_score": rec.confidence_score,
            "created_at": rec.created_at
        }

    # Consenting candidate pool
    consenting_pool_count = db.query(Trainee).filter(Trainee.consent_given == True).count()

    return {
        "company_name": company_name,
        "industry": employer.industry if employer else "Industry Partner",
        "pending_verifications_count": len(pending_records),
        "verified_employees_count": len(verified_records),
        "pending_verifications": [format_item(r) for r in pending_records],
        "verified_hires": [format_item(r) for r in verified_records],
        "candidate_pool_count": consenting_pool_count
    }

@router.post("/verify")
def verify_employment_record(
    action: EmployerVerificationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    emp_record = db.query(EmploymentRecord).filter(EmploymentRecord.id == action.employment_record_id).first()
    if not emp_record:
        raise HTTPException(status_code=404, detail="Employment record not found")

    employer = db.query(Employer).filter(Employer.user_id == current_user.id).first()
    employer_id = employer.id if employer else (emp_record.employer_id or 1)

    status_upper = action.status.upper()
    if status_upper not in ("VERIFIED", "REJECTED"):
        raise HTTPException(status_code=400, detail="Status must be either VERIFIED or REJECTED.")

    calculated_confidence = calculate_verification_confidence(
        status=status_upper,
        reported_salary=emp_record.starting_salary,
        verified_salary=action.verified_salary,
        reported_date=emp_record.joining_date,
        verified_date=action.verified_joining_date,
        employer_is_verified=employer.is_verified if employer else True
    )

    emp_record.verification_status = status_upper
    emp_record.verified_at = datetime.utcnow()
    emp_record.confidence_score = calculated_confidence

    if status_upper == "VERIFIED":
        if action.verified_salary:
            emp_record.starting_salary = action.verified_salary
            emp_record.current_salary = action.verified_salary
        if action.verified_job_title:
            emp_record.job_title = action.verified_job_title

    # Log verification record
    verification_entry = EmployerVerification(
        employment_record_id=emp_record.id,
        employer_id=employer_id,
        verified_by_user_id=current_user.id,
        status=status_upper,
        notes=action.notes,
        verified_salary=action.verified_salary,
        verified_joining_date=action.verified_joining_date,
        verified_job_title=action.verified_job_title,
        confidence_score=calculated_confidence,
        action_timestamp=datetime.utcnow()
    )
    db.add(verification_entry)

    # If verified, record in WageHistory
    if status_upper == "VERIFIED" and action.verified_salary:
        wage = WageHistory(
            trainee_id=emp_record.trainee_id,
            employment_record_id=emp_record.id,
            salary_amount=action.verified_salary,
            currency="INR",
            salary_period="MONTHLY",
            effective_date=action.verified_joining_date or datetime.utcnow().strftime("%Y-%m-%d"),
            source="EMPLOYER_VERIFIED",
            verification_status="VERIFIED",
            notes=action.notes or "Employer verified joining wage"
        )
        db.add(wage)

    db.commit()

    log_audit_event(
        db=db,
        action="EMPLOYMENT_VERIFIED" if status_upper == "VERIFIED" else "EMPLOYMENT_REJECTED",
        entity_type="EMPLOYMENT_RECORD",
        entity_id=str(emp_record.id),
        user_id=current_user.id,
        details={
            "status": status_upper,
            "confidence_score": calculated_confidence,
            "employer_id": employer_id
        }
    )

    return {
        "id": verification_entry.id,
        "employment_record_id": emp_record.id,
        "status": status_upper,
        "confidence_score": calculated_confidence,
        "message": f"Employment successfully {status_upper.lower()} with confidence score {calculated_confidence}."
    }

@router.get("/candidates")
def search_candidates(
    skill: Optional[str] = None,
    location: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Candidate discovery that strictly respects trainee consent and privacy.
    Only exposes non-sensitive information for consenting trainees.
    """
    query = db.query(Trainee).filter(Trainee.consent_given == True)

    if location and location != "ALL":
        query = query.filter((Trainee.district.ilike(f"%{location}%")) | (Trainee.state.ilike(f"%{location}%")))

    trainees = query.limit(50).all()
    results = []
    for t in trainees:
        skills = [s.skill_name for s in t.skills]
        if skill and skill != "ALL" and not any(skill.lower() in s.lower() for s in skills):
            continue

        t_rec = db.query(TrainingRecord).filter(TrainingRecord.trainee_id == t.id).first()
        certs = [c.certificate_number for c in t.certifications]
        emp = db.query(EmploymentRecord).filter(EmploymentRecord.trainee_id == t.id).order_by(EmploymentRecord.created_at.desc()).first()

        results.append({
            "skillpulse_id": t.skillpulse_id,
            "location": f"{t.district or ''}, {t.state or ''}".strip(", "),
            "education": t.education,
            "skills": skills,
            "course_completed": t_rec.course.course_name if t_rec and t_rec.course else None,
            "certifications_count": len(certs),
            "employment_status": emp.status if emp else "SEEKING"
        })

    return results

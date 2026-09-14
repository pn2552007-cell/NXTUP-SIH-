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
from app.services.outcome_access import employer_matches

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
    CORRECTION_REQUESTED keeps the baseline self-reported confidence so the
    trainee can correct the record without it looking employer-confirmed.
    """
    if status == "REJECTED":
        return 0.0
    if status == "CORRECTION_REQUESTED":
        return 0.50

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

    query = db.query(EmploymentRecord).join(Trainee).filter(Trainee.consent_given == True)
    if emp_id:
        # Match by employer_id or company name
        query = query.filter(
            (EmploymentRecord.employer_id == emp_id) |
            ((EmploymentRecord.employer_id.is_(None)) & (EmploymentRecord.employer_name.ilike(company_name)))
        )

    pending_records = query.filter(EmploymentRecord.verification_status == "PENDING").all()
    verified_records = query.filter(EmploymentRecord.verification_status == "VERIFIED").all()

    def format_item(rec: EmploymentRecord):
        tr = rec.trainee
        t_rec = db.query(TrainingRecord).filter(TrainingRecord.trainee_id == tr.id).first() if tr else None
        nid = (tr.nextup_id if tr and tr.nextup_id else (tr.skillpulse_id if tr else None))
        return {
            "id": rec.id,
            "employment_record_id": rec.id,
            "trainee_id": tr.id if tr else None,
            "trainee_name": tr.full_name if tr and tr.consent_given else "Candidate Profile",
            "nextup_id": nid,
            "skillpulse_id": tr.skillpulse_id if tr else None,
            "course_name": t_rec.course.course_name if t_rec and t_rec.course else None,
            "reported_job": rec.job_title,
            "reported_joining_date": rec.joining_date,
            "reported_salary": rec.starting_salary,
            "reported_location": f"{rec.location_city or ''}, {rec.location_state or ''}".strip(", "),
            "verification_status": rec.verification_status,
            "verification_label": (
                "Employer verified" if rec.verification_status == "VERIFIED"
                else "Rejected by employer" if rec.verification_status == "REJECTED"
                else "Correction requested" if rec.verification_status == "CORRECTION_REQUESTED"
                else "Self-reported — awaiting employer verification"
            ),
            "confidence_score": rec.confidence_score,
            "created_at": rec.created_at.isoformat() if rec.created_at else None,
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
    if current_user.role != "EMPLOYER" or not employer_matches(employer, emp_record):
        raise HTTPException(403, "Only the assigned employer can verify this report.")
    if not emp_record.trainee.consent_given:
        raise HTTPException(403, "Active trainee consent is required.")
    if emp_record.status != "EMPLOYED":
        raise HTTPException(400, "Only employed reports can be employer-verified.")
    if emp_record.verification_status != "PENDING":
        raise HTTPException(409, "This report has already been reviewed. A new trainee report is required.")
    employer_id = employer.id
    emp_record.employer_id = employer.id

    status_upper = action.status.upper()
    if status_upper not in ("VERIFIED", "REJECTED", "CORRECTION_REQUESTED"):
        raise HTTPException(status_code=400, detail="Status must be VERIFIED, REJECTED, or CORRECTION_REQUESTED.")
    if status_upper != "VERIFIED" and not (action.notes or "").strip():
        raise HTTPException(400, "Explain what was rejected or needs correction.")

    calculated_confidence = calculate_verification_confidence(
        status=status_upper,
        reported_salary=emp_record.starting_salary,
        verified_salary=action.verified_salary,
        reported_date=emp_record.joining_date,
        verified_date=action.verified_joining_date,
        employer_is_verified=employer.is_verified if employer else True
    )

    # CORRECTION_REQUESTED keeps the record actionable without overwriting verified wage facts.
    if status_upper == "CORRECTION_REQUESTED":
        emp_record.verification_status = "CORRECTION_REQUESTED"
        emp_record.confidence_score = 0.50
    else:
        emp_record.verification_status = status_upper
        emp_record.verified_at = datetime.utcnow() if status_upper == "VERIFIED" else None
        emp_record.confidence_score = calculated_confidence

    if status_upper == "VERIFIED":
        if action.verified_salary:
            emp_record.starting_salary = action.verified_salary
            emp_record.current_salary = action.verified_salary
        if action.verified_job_title:
            emp_record.job_title = action.verified_job_title
            emp_record.job_role = action.verified_job_title
        if action.verified_joining_date:
            emp_record.joining_date = action.verified_joining_date

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
    from app.models.models import Outcome, Followup
    outcome = db.query(Outcome).filter(Outcome.employment_record_id == emp_record.id).first()
    if outcome is None:
        outcome = Outcome(trainee_id=emp_record.trainee_id, employment_record_id=emp_record.id, placement_status=1)
        db.add(outcome)
    outcome.is_verified = status_upper == "VERIFIED"
    outcome.verification_source = "EMPLOYER_PORTAL"
    outcome.verified_at = emp_record.verified_at
    outcome.starting_salary = emp_record.starting_salary
    outcome.current_salary = emp_record.current_salary
    # Confirm only responses linked to this current report, never historical/unrelated check-ins.
    for followup in db.query(Followup).filter(Followup.trainee_id == emp_record.trainee_id, Followup.status == "RESPONDED"):
        response = dict(followup.response_data or {})
        if response.get("employment_record_id") == emp_record.id and response.get("verification_status") == "UNVERIFIED":
            response["verification_status"] = "VERIFIED" if status_upper == "VERIFIED" else "UNVERIFIED"
            response["review_status"] = status_upper
            followup.response_data = response

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
        action=f"EMPLOYMENT_{status_upper}",
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
    if current_user.role not in ("EMPLOYER", "ADMIN"):
        raise HTTPException(403, "Employer role required.")
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

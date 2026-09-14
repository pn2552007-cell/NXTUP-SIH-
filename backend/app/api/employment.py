from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.models import User, Trainee, Employer, EmploymentRecord, TrainingRecord, WageHistory
from app.schemas.schemas import EmploymentReportRequest, EmploymentRecordResponse
from app.auth.jwt_handler import get_current_user
from app.services.notification_service import notification_service
from app.utils.audit import log_audit_event
from app.services.outcome_access import require_trainee_access, employer_matches

router = APIRouter(prefix="/employment", tags=["Employment Tracking"])

def calculate_time_to_employment(db: Session, trainee_id: int, joining_date_str: Optional[str]) -> Optional[int]:
    if not joining_date_str:
        return None
    # Look for completed training record
    training = db.query(TrainingRecord).filter(
        TrainingRecord.trainee_id == trainee_id,
        TrainingRecord.completion_status == "COMPLETED"
    ).order_by(TrainingRecord.end_date.desc()).first()

    if not training or not training.end_date:
        return None

    try:
        t_end = datetime.strptime(training.end_date, "%Y-%m-%d")
        e_join = datetime.strptime(joining_date_str, "%Y-%m-%d")
        days = (e_join - t_end).days
        return max(days, 0)
    except Exception:
        return None

@router.post("", response_model=EmploymentRecordResponse)
def report_employment(
    report: EmploymentReportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    trainee = db.query(Trainee).filter(Trainee.user_id == current_user.id).first()
    if not trainee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trainee profile not found."
        )

    require_trainee_access(db, current_user, trainee, providers=False)
    employer_id = report.employer_id
    if employer_id and not db.query(Employer).filter(Employer.id == employer_id).first():
        raise HTTPException(400, "Selected employer does not exist.")
    if not employer_id and report.employer_name:
        emp = db.query(Employer).filter(Employer.company_name.ilike(report.employer_name.strip())).first()
        if emp:
            employer_id = emp.id

    status_upper = report.status.upper()
    valid_statuses = ("SEEKING", "EMPLOYED", "SELF_EMPLOYED", "NOT_SEEKING", "UNKNOWN")
    if status_upper not in valid_statuses:
        raise HTTPException(400, "Invalid employment status.")

    # Calculate time to employment
    time_to_emp = calculate_time_to_employment(db, trainee.id, report.joining_date)

    emp_record = db.query(EmploymentRecord).filter(EmploymentRecord.trainee_id == trainee.id).first()
    if not emp_record:
        emp_record = EmploymentRecord(trainee_id=trainee.id)
        db.add(emp_record)
        db.flush()

    emp_record.status = status_upper
    emp_record.employer_id = employer_id
    emp_record.employer_name = report.employer_name
    emp_record.job_title = report.job_title
    emp_record.job_role = report.job_role or report.job_title
    emp_record.industry = report.industry
    emp_record.location_city = report.location_city
    emp_record.location_state = report.location_state
    emp_record.employment_type = report.employment_type or "FULL_TIME"
    emp_record.joining_date = report.joining_date
    emp_record.starting_salary = report.starting_salary
    emp_record.current_salary = report.current_salary or report.starting_salary
    emp_record.non_placement_reason = report.non_placement_reason
    emp_record.verification_status = "PENDING"
    emp_record.verified_at = None
    from app.models.models import Outcome
    for outcome in db.query(Outcome).filter(Outcome.employment_record_id == emp_record.id):
        outcome.is_verified = False
        outcome.verified_at = None
    emp_record.confidence_score = 0.50  # Self-reported baseline

    # Add initial wage history if salary provided
    if report.starting_salary and report.starting_salary > 0:
        existing_wage = db.query(WageHistory).filter(WageHistory.trainee_id == trainee.id).first()
        if not existing_wage:
            w_history = WageHistory(
                trainee_id=trainee.id,
                employment_record_id=emp_record.id,
                effective_date=emp_record.joining_date or datetime.utcnow().strftime("%Y-%m-%d"),
                salary_amount=report.starting_salary,
                currency="INR",
                salary_period="MONTHLY",
                source="TRAINEE_REPORTED",
                verification_status="UNVERIFIED",
                growth_pct_since_starting=0.0,
                notes="Self-Reported Initial Joining Salary"
            )
            db.add(w_history)

    db.commit()
    db.refresh(emp_record)

    log_audit_event(
        db=db,
        action="EMPLOYMENT_REPORTED",
        entity_type="EMPLOYMENT_RECORD",
        entity_id=str(emp_record.id),
        user_id=current_user.id,
        details={
            "status": status_upper,
            "employer_name": report.employer_name,
            "starting_salary": report.starting_salary
        }
    )

    # Optional employer notification interface call
    if employer_id:
        linked_employer = db.get(Employer, employer_id)
        notification_service.send_verification_request_to_employer(
            employer_name=report.employer_name,
            employer_email=linked_employer.email,
            trainee_name=trainee.full_name,
            job_title=report.job_title or "Trainee Graduate"
        )

    return EmploymentRecordResponse(
        id=emp_record.id,
        trainee_id=emp_record.trainee_id,
        employer_id=emp_record.employer_id,
        employer_name=emp_record.employer_name,
        job_title=emp_record.job_title,
        job_role=emp_record.job_role,
        industry=emp_record.industry,
        employment_type=emp_record.employment_type,
        location_city=emp_record.location_city,
        location_state=emp_record.location_state,
        joining_date=emp_record.joining_date,
        starting_salary=emp_record.starting_salary,
        current_salary=emp_record.current_salary,
        status=emp_record.status,
        verification_status=emp_record.verification_status,
        confidence_score=emp_record.confidence_score,
        time_to_employment_days=time_to_emp,
        created_at=emp_record.created_at
    )

@router.get("/{record_id}", response_model=EmploymentRecordResponse)
def get_employment_record(record_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    record = db.query(EmploymentRecord).filter(EmploymentRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Employment record not found.")
    if current_user.role == "EMPLOYER":
        employer = db.query(Employer).filter(Employer.user_id == current_user.id).first()
        if not employer_matches(employer, record) or not record.trainee.consent_given:
            raise HTTPException(403, "Employment record is outside your account scope.")
    else:
        require_trainee_access(db, current_user, record.trainee)

    time_to_emp = calculate_time_to_employment(db, record.trainee_id, record.joining_date)

    return EmploymentRecordResponse(
        id=record.id,
        trainee_id=record.trainee_id,
        employer_id=record.employer_id,
        employer_name=record.employer_name,
        job_title=record.job_title,
        job_role=record.job_role,
        industry=record.industry,
        employment_type=record.employment_type,
        location_city=record.location_city,
        location_state=record.location_state,
        joining_date=record.joining_date,
        starting_salary=record.starting_salary,
        current_salary=record.current_salary,
        status=record.status,
        verification_status=record.verification_status,
        confidence_score=record.confidence_score,
        time_to_employment_days=time_to_emp,
        created_at=record.created_at
    )

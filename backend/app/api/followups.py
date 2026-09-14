from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import User, Trainee, Followup, EmploymentRecord, WageHistory
from app.schemas.schemas import FollowupResponse, FollowupRespondRequest
from app.auth.jwt_handler import get_current_user
from app.services.notification_service import notification_service
from app.utils.audit import log_audit_event
from app.services.outcome_access import require_trainee_access

router = APIRouter(prefix="/followups", tags=["Follow-up Longitudinal Tracking"])

@router.get("", response_model=List[FollowupResponse])
def get_trainee_followups(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    trainee = db.query(Trainee).filter(Trainee.user_id == current_user.id).first()
    if not trainee and current_user.role != "ADMIN":
        return []

    query = db.query(Followup)
    if trainee:
        query = query.filter(Followup.trainee_id == trainee.id)
    return query.order_by(Followup.id.asc()).all()

@router.post("/schedule")
def schedule_followups(
    trainee_id: Optional[int] = None,
    base_date: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Schedules longitudinal checkpoints (30 days, 90 days, 6 months, 12 months)
    for a trainee post-training or post-placement.
    """
    if trainee_id is None:
        t = db.query(Trainee).filter(Trainee.user_id == current_user.id).first()
        if not t:
            raise HTTPException(status_code=404, detail="Trainee profile not found.")
        trainee = t
    else:
        trainee = db.query(Trainee).filter(Trainee.id == trainee_id).first()
        if not trainee:
            raise HTTPException(status_code=404, detail="Trainee not found.")

    require_trainee_access(db, current_user, trainee)
    checkpoints = [
        ("30_DAYS", 30),
        ("90_DAYS", 90),
        ("6_MONTHS", 180),
        ("12_MONTHS", 365)
    ]

    from datetime import timedelta
    try:
        start = datetime.strptime(base_date, "%Y-%m-%d") if base_date else datetime.utcnow()
    except ValueError:
        raise HTTPException(400, "base_date must be YYYY-MM-DD.")

    scheduled = []
    for cp_name, days in checkpoints:
        sched_date = (start + timedelta(days=days)).strftime("%Y-%m-%d")
        existing = db.query(Followup).filter(
            Followup.trainee_id == trainee.id,
            Followup.checkpoint == cp_name
        ).first()
        if not existing:
            fup = Followup(
                trainee_id=trainee.id,
                checkpoint=cp_name,
                status="SCHEDULED",
                scheduled_date=sched_date,
                channel="PORTAL"
            )
            db.add(fup)
            scheduled.append(fup)

    db.commit()

    log_audit_event(
        db=db,
        action="FOLLOWUPS_SCHEDULED",
        entity_type="TRAINEE",
        entity_id=str(trainee.id),
        user_id=current_user.id,
        details={"scheduled_count": len(scheduled)}
    )

    return {"message": f"Successfully scheduled {len(scheduled)} longitudinal follow-up checkpoints."}

@router.post("/send/{followup_id}", response_model=FollowupResponse)
def send_followup(
    followup_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Move a scheduled checkpoint to SENT: Pending → Sent → Responded → Verified/Unverified."""
    fup = db.query(Followup).filter(Followup.id == followup_id).first()
    if not fup:
        raise HTTPException(status_code=404, detail="Follow-up record not found.")
    if fup.status not in ("SCHEDULED", "PENDING"):
        raise HTTPException(status_code=400, detail=f"Only scheduled follow-ups can be sent (current: {fup.status}).")
    require_trainee_access(db, current_user, fup.trainee)
    fup.status = "SENT"
    fup.channel = "PORTAL"
    fup.sent_message = "A consent-based outcome check-in is available in your NXTUP portal. No SMS or WhatsApp was sent."
    fup.sent_at = datetime.utcnow()
    db.commit()
    db.refresh(fup)
    log_audit_event(
        db=db,
        action="FOLLOWUP_SENT",
        entity_type="FOLLOWUP",
        entity_id=str(fup.id),
        user_id=current_user.id,
        details={"checkpoint": fup.checkpoint, "channel": fup.channel},
    )
    return fup

@router.post("/respond", response_model=FollowupResponse)
def respond_to_followup(
    payload: FollowupRespondRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    fup = db.query(Followup).filter(Followup.id == payload.followup_id).first()
    if not fup:
        raise HTTPException(status_code=404, detail="Follow-up record not found.")

    require_trainee_access(db, current_user, fup.trainee, providers=False)
    now = datetime.utcnow()
    fup.status = "RESPONDED"
    fup.responded_at = now
    fup.response_data = {
        "employed": payload.employed,
        "employer_name": payload.employer_name,
        "job_title": payload.job_title,
        "current_salary": payload.current_salary,
        "satisfaction_score": payload.satisfaction_score,
        "skills_used": payload.skills_used or [],
        "verification_status": "UNVERIFIED",
    }

    # Update employment and wage history if salary reported
    emp = db.query(EmploymentRecord).filter(EmploymentRecord.trainee_id == fup.trainee_id).first()
    if emp:
        emp.verification_status = "PENDING"
        emp.verified_at = None
        emp.confidence_score = 0.5
        from app.models.models import Outcome, Employer
        for outcome in db.query(Outcome).filter(Outcome.employment_record_id == emp.id):
            outcome.is_verified = False
            outcome.verified_at = None
        fup.response_data = {**fup.response_data, "employment_record_id": emp.id}
        if payload.employed:
            emp.status = "EMPLOYED"
            if payload.employer_name:
                emp.employer_name = payload.employer_name
                linked = db.query(Employer).filter(Employer.company_name.ilike(payload.employer_name.strip())).first()
                emp.employer_id = linked.id if linked else None
            if payload.job_title:
                emp.job_title = payload.job_title
            if payload.current_salary:
                emp.current_salary = payload.current_salary
        else:
            emp.status = "SEEKING"

    if payload.current_salary and payload.current_salary > 0:
        starting = emp.starting_salary if emp and emp.starting_salary else payload.current_salary
        growth_pct = round(((payload.current_salary - starting) / starting) * 100.0, 1) if starting > 0 else 0.0

        wage_entry = WageHistory(
            trainee_id=fup.trainee_id,
            employment_record_id=emp.id if emp else None,
            effective_date=now.strftime("%Y-%m-%d"),
            salary_amount=payload.current_salary,
            currency="INR",
            salary_period="MONTHLY",
            source="FOLLOWUP",
            verification_status="UNVERIFIED",
            growth_pct_since_starting=growth_pct,
            notes=f"Longitudinal outcome at {fup.checkpoint.replace('_', ' ').title()}"
        )
        db.add(wage_entry)

    db.commit()
    db.refresh(fup)

    log_audit_event(
        db=db,
        action="FOLLOWUP_RECORDED",
        entity_type="FOLLOWUP",
        entity_id=str(fup.id),
        user_id=current_user.id,
        details={"checkpoint": fup.checkpoint, "employed": payload.employed}
    )

    return fup

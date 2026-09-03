from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from app.database import get_db
from app.models.models import (
    User, Trainee, TrainingRecord, Assessment, Certification,
    TraineeSkill, EmploymentRecord, Followup, WageHistory, SkillGapAnalysis
)
from app.schemas.schemas import (
    TraineeResponse, TraineeSkillCreate, TraineeSkillResponse,
    WageGrowthResponse, WageHistoryEntry
)
from app.auth.jwt_handler import get_current_user
from app.utils.skill_normalizer import normalize_skill_name, get_or_create_skill
from app.utils.audit import log_audit_event
router = APIRouter(prefix="/trainee", tags=["Trainee Profile & Journey"])

@router.get("/profile")
def get_trainee_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "TRAINEE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: Trainee role required."
        )

    trainee = db.query(Trainee).filter(Trainee.user_id == current_user.id).first()
    if not trainee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trainee profile not found for this account."
        )

    t_record = db.query(TrainingRecord).filter(TrainingRecord.trainee_id == trainee.id).first()
    assessment = db.query(Assessment).filter(Assessment.trainee_id == trainee.id).order_by(Assessment.created_at.desc()).first()
    cert = db.query(Certification).filter(Certification.trainee_id == trainee.id).first()
    emp_record = db.query(EmploymentRecord).filter(EmploymentRecord.trainee_id == trainee.id).order_by(EmploymentRecord.created_at.desc()).first()
    gap_record = db.query(SkillGapAnalysis).filter(SkillGapAnalysis.trainee_id == trainee.id).order_by(SkillGapAnalysis.created_at.desc()).first()

    starting_sal = emp_record.starting_salary if emp_record and emp_record.starting_salary else None
    current_sal = emp_record.current_salary if emp_record and emp_record.current_salary else starting_sal
    wage_growth = None
    if starting_sal and current_sal and starting_sal > 0:
        wage_growth = round(((current_sal - starting_sal) / starting_sal) * 100.0, 1)

    # Longitudinal retention from actual records
    retention_6m = None
    retention_12m = None
    if emp_record and emp_record.status == "EMPLOYED":
        fup_6m = db.query(Followup).filter(Followup.trainee_id == trainee.id, Followup.checkpoint == "6_MONTHS").first()
        if fup_6m and fup_6m.status == "RESPONDED":
            res_data = fup_6m.response_data or {}
            retention_6m = bool(res_data.get("employed", True))

        fup_12m = db.query(Followup).filter(Followup.trainee_id == trainee.id, Followup.checkpoint == "12_MONTHS").first()
        if fup_12m and fup_12m.status == "RESPONDED":
            res_data = fup_12m.response_data or {}
            retention_12m = bool(res_data.get("employed", True))

    return {
        "id": trainee.id,
        "skillpulse_id": trainee.skillpulse_id,
        "full_name": trainee.full_name,
        "email": trainee.email,
        "phone": trainee.phone,
        "state": trainee.state,
        "district": trainee.district,
        "education": trainee.education,
        "gender": trainee.gender,
        "date_of_birth": trainee.date_of_birth,
        "consent_given": trainee.consent_given,
        "created_at": trainee.created_at,
        "course_name": t_record.course.course_name if t_record and t_record.course else None,
        "provider_name": t_record.provider.organization_name if t_record and t_record.provider else None,
        "training_completion": t_record.completion_status if t_record else "NO_TRAINING_RECORD",
        "attendance_pct": t_record.attendance_pct if t_record else None,
        "assessment_score": assessment.score if assessment else None,
        "certification_status": cert.status if cert else None,
        "certificate_number": cert.certificate_number if cert else None,
        "employment_status": emp_record.status if emp_record else "NOT_REPORTED",
        "current_job": emp_record.job_title if emp_record else None,
        "current_employer": emp_record.employer_name if emp_record else None,
        "starting_salary": starting_sal,
        "current_salary": current_sal,
        "wage_growth_pct": wage_growth,
        "retention_6m": retention_6m,
        "retention_12m": retention_12m,
        "skill_gap_score": gap_record.skill_gap_score if gap_record else None,
        "confidence_score": emp_record.confidence_score if emp_record else None,
        "verification_status": emp_record.verification_status if emp_record else None
    }

@router.get("/journey")
def get_trainee_journey(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    trainee = db.query(Trainee).filter(Trainee.user_id == current_user.id).first()
    if not trainee:
        raise HTTPException(status_code=404, detail="Trainee profile not found")

    t_record = db.query(TrainingRecord).filter(TrainingRecord.trainee_id == trainee.id).first()
    assessment = db.query(Assessment).filter(Assessment.trainee_id == trainee.id).first()
    cert = db.query(Certification).filter(Certification.trainee_id == trainee.id).first()
    emp_record = db.query(EmploymentRecord).filter(EmploymentRecord.trainee_id == trainee.id).first()
    wage_records = db.query(WageHistory).filter(WageHistory.trainee_id == trainee.id).order_by(WageHistory.effective_date.asc()).all()

    milestones = [
        {
            "step": "CONSENT",
            "title": "Trainee Consent & ID Activation",
            "status": "COMPLETED" if trainee.consent_given else "PENDING",
            "date": trainee.created_at.strftime("%Y-%m-%d") if trainee.created_at else None,
            "details": {"skillpulse_id": trainee.skillpulse_id, "consent_status": trainee.consent_given}
        },
        {
            "step": "TRAINING",
            "title": "Vocational & Technical Training",
            "status": t_record.completion_status if t_record else "NOT_STARTED",
            "date": t_record.end_date if t_record else None,
            "details": {
                "course": t_record.course.course_name if t_record and t_record.course else "No course enrolled",
                "attendance": f"{t_record.attendance_pct}%" if t_record else None
            }
        },
        {
            "step": "CERTIFICATION",
            "title": "Skill Assessment & Certification",
            "status": cert.status if cert else ("IN_PROGRESS" if assessment else "NOT_STARTED"),
            "date": cert.issue_date if cert else None,
            "details": {
                "score": f"{assessment.score}/{assessment.max_score}" if assessment else None,
                "cert_no": cert.certificate_number if cert else None
            }
        },
        {
            "step": "EMPLOYMENT",
            "title": "Post-Certification Employment Placement",
            "status": emp_record.status if emp_record else "NOT_STARTED",
            "date": emp_record.joining_date if emp_record else None,
            "details": {
                "employer": emp_record.employer_name if emp_record else None,
                "role": emp_record.job_title if emp_record else None,
                "verified": emp_record.verification_status if emp_record else "PENDING",
                "confidence": f"{int((emp_record.confidence_score or 0.0)*100)}%" if emp_record else None
            }
        },
        {
            "step": "RETENTION_6M",
            "title": "6-Month Retention Verification",
            "status": "COMPLETED" if (emp_record and emp_record.status == "EMPLOYED") else "PENDING",
            "date": None,
            "details": {"status": "Awaiting longitudinal checkpoint" if not emp_record else "Tracking active"}
        },
        {
            "step": "WAGE_GROWTH",
            "title": "Longitudinal Wage Progression",
            "status": "COMPLETED" if len(wage_records) > 1 else "IN_PROGRESS",
            "date": None,
            "details": {
                "starting": f"₹{int(emp_record.starting_salary):,}" if emp_record and emp_record.starting_salary else None,
                "current": f"₹{int(emp_record.current_salary):,}" if emp_record and emp_record.current_salary else None,
                "growth": f"+{round(((emp_record.current_salary - emp_record.starting_salary)/emp_record.starting_salary)*100, 1)}%" if emp_record and emp_record.starting_salary and emp_record.current_salary and emp_record.starting_salary > 0 else None
            }
        }
    ]
    return milestones

@router.get("/skills")
def get_trainee_skills(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    trainee = db.query(Trainee).filter(Trainee.user_id == current_user.id).first()
    if not trainee:
        raise HTTPException(status_code=404, detail="Trainee profile not found")

    skills = db.query(TraineeSkill).filter(TraineeSkill.trainee_id == trainee.id).all()
    return [{"id": s.id, "skill_name": s.skill_name, "proficiency_level": s.proficiency_level, "is_verified": s.is_verified} for s in skills]

@router.post("/skills", response_model=TraineeSkillResponse)
def add_trainee_skill(
    skill_in: TraineeSkillCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    trainee = db.query(Trainee).filter(Trainee.user_id == current_user.id).first()
    if not trainee:
        raise HTTPException(status_code=404, detail="Trainee profile not found")

    norm_name = normalize_skill_name(skill_in.skill_name)
    if not norm_name:
        raise HTTPException(status_code=400, detail="Skill name cannot be empty.")

    # Check if already added
    existing = db.query(TraineeSkill).filter(
        TraineeSkill.trainee_id == trainee.id,
        TraineeSkill.skill_name.ilike(norm_name)
    ).first()
    if existing:
        existing.proficiency_level = skill_in.proficiency_level or "INTERMEDIATE"
        db.commit()
        db.refresh(existing)
        return existing

    # Normalization lookup or insertion
    global_skill = get_or_create_skill(db, norm_name)

    trainee_skill = TraineeSkill(
        trainee_id=trainee.id,
        skill_id=global_skill.id if global_skill else None,
        skill_name=norm_name,
        proficiency_level=skill_in.proficiency_level or "INTERMEDIATE",
        is_verified=False
    )
    db.add(trainee_skill)
    db.commit()
    db.refresh(trainee_skill)

    log_audit_event(
        db=db,
        action="SKILL_ADDED",
        entity_type="TRAINEE_SKILL",
        entity_id=str(trainee_skill.id),
        user_id=current_user.id,
        details={"skill": norm_name, "trainee_id": trainee.id}
    )

    return trainee_skill

@router.get("/wage-growth", response_model=WageGrowthResponse)
def get_trainee_wage_growth(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    trainee = db.query(Trainee).filter(Trainee.user_id == current_user.id).first()
    if not trainee:
        raise HTTPException(status_code=404, detail="Trainee profile not found")

    emp = db.query(EmploymentRecord).filter(EmploymentRecord.trainee_id == trainee.id).order_by(EmploymentRecord.created_at.desc()).first()
    histories = db.query(WageHistory).filter(WageHistory.trainee_id == trainee.id).order_by(WageHistory.effective_date.asc()).all()

    if not histories and not emp:
        return WageGrowthResponse(
            trainee_id=trainee.id,
            starting_salary=None,
            current_salary=None,
            overall_growth_pct=None,
            history=[],
            has_history=False,
            message="No wage history available."
        )

    starting = emp.starting_salary if emp and emp.starting_salary else (histories[0].salary_amount if histories else None)
    current = emp.current_salary if emp and emp.current_salary else (histories[-1].salary_amount if histories else starting)
    growth_pct = None
    if starting and current and starting > 0:
        growth_pct = round(((current - starting) / starting) * 100.0, 1)

    items = [
        WageHistoryEntry(
            id=h.id,
            effective_date=h.effective_date,
            salary_amount=h.salary_amount,
            growth_pct_since_starting=h.growth_pct_since_starting,
            source=h.source,
            verification_status=h.verification_status,
            notes=h.notes
        ) for h in histories
    ]

    return WageGrowthResponse(
        trainee_id=trainee.id,
        starting_salary=starting,
        current_salary=current,
        overall_growth_pct=growth_pct,
        history=items,
        has_history=len(items) > 0,
        message=None if len(items) > 0 else "No wage history available."
    )

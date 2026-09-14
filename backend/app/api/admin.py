"""
NEXTUP Admin Panel API
----------------------
All endpoints require ADMIN role JWT authentication.
All metrics are computed from live PostgreSQL data.
No fake/hardcoded statistics.
"""
from typing import List, Optional, Any, Dict
from datetime import datetime, date
from collections import Counter
import csv
import io

from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, case, desc, asc, or_

from app.database import get_db
from app.models.models import (
    User, Trainee, Provider, Employer, Course, TrainingBatch,
    Enrollment, TrainingRecord, Assessment, Certification,
    TraineeSkill, EmploymentRecord, EmployerVerification,
    Followup, WageHistory, SkillGapAnalysis, AuditLog
)
from app.auth.jwt_handler import get_current_user, require_role
from app.utils.audit import log_audit_event

router = APIRouter(prefix="/admin", tags=["Admin Panel"])

# ─────────────────────────────────────────────
# Dependency shorthand for ADMIN-only routes
# ─────────────────────────────────────────────
admin_required = require_role(["ADMIN"])


# ══════════════════════════════════════════════
# 1. DASHBOARD — Real-time database metrics
# ══════════════════════════════════════════════

@router.get("/dashboard")
def admin_dashboard(
    state: Optional[str] = None, district: Optional[str] = None,
    provider_id: Optional[int] = None, course_id: Optional[int] = None,
    cohort: Optional[str] = None, start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(admin_required), db: Session = Depends(get_db)
):
    from app.services.outcome_metrics import dashboard_metrics
    if start_date and end_date and start_date > end_date:
        raise HTTPException(400, "Start date must not follow end date.")
    return dashboard_metrics(db, state, district, provider_id, course_id, cohort, start_date, end_date)


@router.get("/filters")
def get_available_filters(
    state: Optional[str] = None,
    district: Optional[str] = None,
    provider_id: Optional[int] = None,
    course_id: Optional[int] = None,
    current_user: User = Depends(admin_required),
    db: Session = Depends(get_db)
):
    trainee_q = db.query(Trainee)
    if state and state != "ALL":
        trainee_q = trainee_q.filter(Trainee.state == state)
    if district and district != "ALL":
        trainee_q = trainee_q.filter(Trainee.district == district)

    states = [s[0] for s in db.query(Trainee.state).distinct().filter(Trainee.state.isnot(None)).all()]
    districts = [d[0] for d in trainee_q.with_entities(Trainee.district).distinct().filter(Trainee.district.isnot(None)).all()]

    provider_q = db.query(Provider)
    if state and state != "ALL":
        provider_q = provider_q.filter(Provider.state == state)
    providers = [{"id": p.id, "name": p.organization_name} for p in provider_q.order_by(Provider.organization_name).all()]

    course_q = db.query(Course)
    if provider_id:
        course_q = course_q.filter(Course.provider_id == provider_id)
    courses = [{"id": c.id, "name": c.course_name, "domain": c.domain} for c in course_q.order_by(Course.course_name).all()]

    cohort_q = db.query(TrainingRecord.cohort_id).distinct().filter(TrainingRecord.cohort_id.isnot(None))
    if provider_id:
        cohort_q = cohort_q.filter(TrainingRecord.provider_id == provider_id)
    if course_id:
        cohort_q = cohort_q.filter(TrainingRecord.course_id == course_id)
    cohorts = [c[0] for c in cohort_q.all()]
    employers = [{"id": e.id, "name": e.company_name} for e in db.query(Employer).all()]

    return {
        "states": ["ALL"] + sorted(states),
        "districts": ["ALL"] + sorted(districts),
        "providers": providers,
        "courses": courses,
        "cohorts": ["ALL"] + sorted(cohorts),
        "employers": employers
    }


# ══════════════════════════════════════════════
# 2. TRAINEES — Management & Profiles
# ══════════════════════════════════════════════

@router.get("/trainees")
def list_trainees(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    state: Optional[str] = None,
    district: Optional[str] = None,
    training_status: Optional[str] = None,
    employment_status: Optional[str] = None,
    cert_status: Optional[str] = None,
    sort_by: str = "created_at",
    sort_dir: str = "desc",
    current_user: User = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """Paginated trainee list with search, filter, sort."""
    q = db.query(Trainee)

    if search:
        like = f"%{search}%"
        q = q.filter(or_(
            Trainee.full_name.ilike(like),
            Trainee.email.ilike(like),
            Trainee.nextup_id.ilike(like),
            Trainee.skillpulse_id.ilike(like),
            Trainee.phone.ilike(like)
        ))
    if state and state != "ALL":
        q = q.filter(Trainee.state == state)
    if district and district != "ALL":
        q = q.filter(Trainee.district == district)

    # Sort
    sort_col = getattr(Trainee, sort_by, Trainee.created_at)
    q = q.order_by(desc(sort_col) if sort_dir == "desc" else asc(sort_col))

    total = q.count()
    trainees = q.offset((page - 1) * per_page).limit(per_page).all()

    rows = []
    for t in trainees:
        t_record = db.query(TrainingRecord).filter(TrainingRecord.trainee_id == t.id).first()
        cert = db.query(Certification).filter(Certification.trainee_id == t.id).first()
        emp = db.query(EmploymentRecord).filter(EmploymentRecord.trainee_id == t.id).first()

        # Filters
        if training_status and training_status != "ALL":
            tr_stat = t_record.completion_status if t_record else "NOT_STARTED"
            if tr_stat != training_status:
                continue
        if employment_status and employment_status != "ALL":
            emp_stat = emp.status if emp else "NOT_REPORTED"
            if emp_stat != employment_status:
                continue
        if cert_status and cert_status != "ALL":
            c_stat = cert.status if cert else "NOT_ISSUED"
            if c_stat != cert_status:
                continue

        rows.append({
            "id": t.id,
            "nextup_id": t.nextup_id or t.skillpulse_id,
            "skillpulse_id": t.nextup_id or t.skillpulse_id,
            "full_name": t.full_name,
            "email": t.email,
            "phone": t.phone,
            "state": t.state,
            "district": t.district,
            "gender": t.gender,
            "education": t.education,
            "consent_given": t.consent_given,
            "created_at": t.created_at.isoformat() if t.created_at else None,
            "course_name": t_record.course.course_name if t_record and t_record.course else None,
            "provider_name": t_record.provider.organization_name if t_record and t_record.provider else None,
            "training_status": t_record.completion_status if t_record else "NOT_STARTED",
            "certificate_status": cert.status if cert else "NOT_ISSUED",
            "employment_status": emp.status if emp else "NOT_REPORTED",
            "employer_name": emp.employer_name if emp else None,
            "verification_status": emp.verification_status if emp else None,
        })

    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": max(1, (total + per_page - 1) // per_page),
        "items": rows
    }


@router.get("/trainees/{trainee_id}")
def get_trainee_detail(
    trainee_id: int,
    current_user: User = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """Full trainee profile for admin — all tabs."""
    trainee = db.query(Trainee).filter(Trainee.id == trainee_id).first()
    if not trainee:
        raise HTTPException(status_code=404, detail="Trainee not found")

    log_audit_event(
        db=db, action="ADMIN_PROFILE_ACCESS", entity_type="TRAINEE",
        entity_id=str(trainee_id), user_id=current_user.id,
        details={"skillpulse_id": trainee.skillpulse_id}
    )

    training_records = db.query(TrainingRecord).filter(TrainingRecord.trainee_id == trainee_id).all()
    assessments = db.query(Assessment).filter(Assessment.trainee_id == trainee_id).all()
    certifications = db.query(Certification).filter(Certification.trainee_id == trainee_id).all()
    skills = db.query(TraineeSkill).filter(TraineeSkill.trainee_id == trainee_id).all()
    employment_records = db.query(EmploymentRecord).filter(EmploymentRecord.trainee_id == trainee_id).all()
    followups = db.query(Followup).filter(Followup.trainee_id == trainee_id).order_by(Followup.created_at).all()
    wage_history = db.query(WageHistory).filter(WageHistory.trainee_id == trainee_id).order_by(WageHistory.effective_date).all()

    # Employer verifications for this trainee
    emp_ids = [e.id for e in employment_records]
    verifications = db.query(EmployerVerification).filter(
        EmployerVerification.employment_record_id.in_(emp_ids)
    ).all() if emp_ids else []

    return {
        "profile": {
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
            "created_at": trainee.created_at.isoformat() if trainee.created_at else None,
        },
        "training": [
            {
                "id": r.id,
                "course": r.course.course_name if r.course else None,
                "provider": r.provider.organization_name if r.provider else None,
                "batch_code": r.batch.batch_code if r.batch else None,
                "start_date": r.start_date,
                "end_date": r.end_date,
                "completion_status": r.completion_status,
                "attendance_pct": r.attendance_pct,
            } for r in training_records
        ],
        "skills": [
            {
                "id": s.id,
                "skill_name": s.skill_name,
                "proficiency_level": s.proficiency_level,
                "is_verified": s.is_verified,
            } for s in skills
        ],
        "assessments": [
            {
                "id": a.id,
                "assessment_name": a.assessment_name,
                "skill_name": a.skill_name,
                "assessment_type": a.assessment_type,
                "score": a.score,
                "max_score": a.max_score,
                "percentage": a.percentage,
                "pass_status": a.pass_status,
                "date_taken": a.date_taken,
            } for a in assessments
        ],
        "certifications": [
            {
                "id": c.id,
                "certificate_number": c.certificate_number,
                "course": c.course.course_name if c.course else None,
                "issuing_organization": c.issuing_organization,
                "issue_date": c.issue_date,
                "expiry_date": c.expiry_date,
                "certificate_url": c.certificate_url,
                "status": c.status,
                "related_skills": c.related_skills,
                "created_at": c.created_at.isoformat() if c.created_at else None,
            } for c in certifications
        ],
        "employment": [
            {
                "id": e.id,
                "employer_name": e.employer_name,
                "job_title": e.job_title,
                "job_role": e.job_role,
                "industry": e.industry,
                "employment_type": e.employment_type,
                "location_city": e.location_city,
                "location_state": e.location_state,
                "joining_date": e.joining_date,
                "starting_salary": e.starting_salary,
                "current_salary": e.current_salary,
                "status": e.status,
                "verification_status": e.verification_status,
                "confidence_score": e.confidence_score,
                "created_at": e.created_at.isoformat() if e.created_at else None,
            } for e in employment_records
        ],
        "verifications": [
            {
                "id": v.id,
                "employment_record_id": v.employment_record_id,
                "status": v.status,
                "notes": v.notes,
                "verified_salary": v.verified_salary,
                "verified_joining_date": v.verified_joining_date,
                "verified_job_title": v.verified_job_title,
                "confidence_score": v.confidence_score,
                "action_timestamp": v.action_timestamp.isoformat() if v.action_timestamp else None,
            } for v in verifications
        ],
        "followups": [
            {
                "id": f.id,
                "checkpoint": f.checkpoint,
                "status": f.status,
                "scheduled_date": f.scheduled_date,
                "sent_at": f.sent_at.isoformat() if f.sent_at else None,
                "responded_at": f.responded_at.isoformat() if f.responded_at else None,
                "response_data": f.response_data,
                "channel": f.channel,
            } for f in followups
        ],
        "wage_history": [
            {
                "id": w.id,
                "effective_date": w.effective_date,
                "salary_amount": w.salary_amount,
                "currency": w.currency,
                "salary_period": w.salary_period,
                "growth_pct_since_starting": w.growth_pct_since_starting,
                "source": w.source,
                "verification_status": w.verification_status,
                "notes": w.notes,
            } for w in wage_history
        ],
        "consent": {
            "consent_given": trainee.consent_given,
        }
    }


# ══════════════════════════════════════════════
# 3. USERS — Management
# ══════════════════════════════════════════════

@router.get("/users")
def list_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    sort_by: str = "created_at",
    sort_dir: str = "desc",
    current_user: User = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """All users — NO passwords or tokens returned."""
    q = db.query(User)

    if search:
        like = f"%{search}%"
        q = q.filter(or_(
            User.full_name.ilike(like),
            User.email.ilike(like),
            User.phone.ilike(like)
        ))
    if role and role != "ALL":
        q = q.filter(User.role == role)
    if is_active is not None:
        q = q.filter(User.is_active == is_active)

    sort_col = getattr(User, sort_by, User.created_at)
    q = q.order_by(desc(sort_col) if sort_dir == "desc" else asc(sort_col))

    total = q.count()
    users = q.offset((page - 1) * per_page).limit(per_page).all()

    # Last login from audit logs
    rows = []
    for u in users:
        last_login = db.query(AuditLog.created_at).filter(
            AuditLog.user_id == u.id,
            AuditLog.action == "LOGIN"
        ).order_by(desc(AuditLog.created_at)).first()

        skillpulse_id = None
        nextup_id = None
        if u.trainee_profile:
            nextup_id = u.trainee_profile.nextup_id or u.trainee_profile.skillpulse_id
            skillpulse_id = nextup_id

        rows.append({
            "id": u.id,
            "full_name": u.full_name,
            "email": u.email,
            "phone": u.phone,
            "role": u.role,
            "is_active": u.is_active,
            "created_at": u.created_at.isoformat() if u.created_at else None,
            "last_login": last_login[0].isoformat() if last_login else None,
            "nextup_id": nextup_id,
            "skillpulse_id": skillpulse_id,
        })

    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": max(1, (total + per_page - 1) // per_page),
        "items": rows
    }


@router.patch("/users/{user_id}")
def update_user(
    user_id: int,
    payload: Dict[str, Any],
    current_user: User = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """Admin can update role and/or active status. Cannot change own role."""
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Admins cannot modify their own account via this endpoint.")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    allowed_roles = {"TRAINEE", "TRAINING_PROVIDER", "EMPLOYER", "ADMIN"}
    old_role = user.role
    old_active = user.is_active

    if "role" in payload:
        new_role = payload["role"].upper()
        if new_role not in allowed_roles:
            raise HTTPException(status_code=400, detail=f"Invalid role: {new_role}")
        user.role = new_role

    if "is_active" in payload:
        user.is_active = bool(payload["is_active"])

    db.commit()
    db.refresh(user)

    log_audit_event(
        db=db, action="ADMIN_USER_UPDATE", entity_type="USER",
        entity_id=str(user_id), user_id=current_user.id,
        details={
            "old_role": old_role, "new_role": user.role,
            "old_active": old_active, "new_active": user.is_active
        }
    )

    return {"message": "User updated", "user_id": user_id, "role": user.role, "is_active": user.is_active}


# ══════════════════════════════════════════════
# 4. TRAINING & COURSES
# ══════════════════════════════════════════════

@router.get("/training")
def admin_training_overview(
    current_user: User = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """Courses, providers, batches — real counts and rates."""
    total_courses = db.query(func.count(Course.id)).scalar() or 0
    total_providers = db.query(func.count(Provider.id)).scalar() or 0
    total_batches = db.query(func.count(TrainingBatch.id)).scalar() or 0
    total_enrolled = db.query(func.count(TrainingRecord.id)).scalar() or 0
    total_completed = db.query(func.count(TrainingRecord.id)).filter(
        TrainingRecord.completion_status == "COMPLETED"
    ).scalar() or 0

    completion_rate = round((total_completed / max(total_enrolled, 1)) * 100.0, 1) if total_enrolled > 0 else 0.0

    courses = db.query(Course).all()
    course_rows = []
    for c in courses:
        enrolled = db.query(func.count(TrainingRecord.id)).filter(TrainingRecord.course_id == c.id).scalar() or 0
        completed = db.query(func.count(TrainingRecord.id)).filter(
            TrainingRecord.course_id == c.id,
            TrainingRecord.completion_status == "COMPLETED"
        ).scalar() or 0
        t_ids = [r.trainee_id for r in db.query(TrainingRecord.trainee_id).filter(TrainingRecord.course_id == c.id).all()]
        employed = db.query(func.count(EmploymentRecord.id)).filter(
            EmploymentRecord.trainee_id.in_(t_ids), EmploymentRecord.status == "EMPLOYED"
        ).scalar() if t_ids else 0

        course_rows.append({
            "id": c.id,
            "course_name": c.course_name,
            "domain": c.domain,
            "duration_weeks": c.duration_weeks,
            "provider_id": c.provider_id,
            "provider_name": c.provider.organization_name if c.provider else None,
            "enrolled": enrolled,
            "completed": completed,
            "employed": employed,
            "completion_rate": round((completed / max(enrolled, 1)) * 100.0, 1) if enrolled > 0 else 0.0,
            "employment_rate": round((employed / max(enrolled, 1)) * 100.0, 1) if enrolled > 0 else 0.0,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        })

    providers = db.query(Provider).all()
    provider_rows = []
    for p in providers:
        trained = db.query(func.count(TrainingRecord.id)).filter(TrainingRecord.provider_id == p.id).scalar() or 0
        provider_rows.append({
            "id": p.id,
            "organization_name": p.organization_name,
            "state": p.state,
            "district": p.district,
            "total_courses": db.query(func.count(Course.id)).filter(Course.provider_id == p.id).scalar() or 0,
            "total_batches": db.query(func.count(TrainingBatch.id)).filter(TrainingBatch.provider_id == p.id).scalar() or 0,
            "total_trained": trained,
            "created_at": p.created_at.isoformat() if p.created_at else None,
        })

    return {
        "summary": {
            "total_courses": total_courses,
            "total_providers": total_providers,
            "total_batches": total_batches,
            "total_enrolled": total_enrolled,
            "total_completed": total_completed,
            "completion_rate_pct": completion_rate,
        },
        "courses": course_rows,
        "providers": provider_rows
    }


# ══════════════════════════════════════════════
# 5. CERTIFICATES
# ══════════════════════════════════════════════

@router.get("/certificates")
def list_certificates(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: User = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """All certificates with trainee info."""
    q = db.query(Certification)

    if search:
        like = f"%{search}%"
        q = q.filter(or_(
            Certification.certificate_number.ilike(like),
            Certification.issuing_organization.ilike(like)
        ))
    if status_filter and status_filter != "ALL":
        q = q.filter(Certification.status == status_filter)

    total = q.count()
    certs = q.order_by(desc(Certification.created_at)).offset((page - 1) * per_page).limit(per_page).all()

    rows = []
    for c in certs:
        trainee = db.query(Trainee).filter(Trainee.id == c.trainee_id).first()
        rows.append({
            "id": c.id,
            "trainee_id": c.trainee_id,
            "trainee_name": trainee.full_name if trainee else None,
            "skillpulse_id": trainee.skillpulse_id if trainee else None,
            "certificate_number": c.certificate_number,
            "course_name": c.course.course_name if c.course else None,
            "issuing_organization": c.issuing_organization,
            "issue_date": c.issue_date,
            "expiry_date": c.expiry_date,
            "certificate_url": c.certificate_url,
            "related_skills": c.related_skills,
            "status": c.status,
            "upload_date": c.created_at.isoformat() if c.created_at else None,
        })

    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": max(1, (total + per_page - 1) // per_page),
        "items": rows
    }


@router.patch("/certificates/{cert_id}")
def update_certificate(
    cert_id: int,
    payload: Dict[str, Any],
    current_user: User = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """Admin updates certificate status (ISSUED → REVOKED/EXPIRED)."""
    cert = db.query(Certification).filter(Certification.id == cert_id).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")

    allowed_statuses = {"ISSUED", "REVOKED", "EXPIRED"}
    if "status" in payload:
        if payload["status"].upper() not in allowed_statuses:
            raise HTTPException(status_code=400, detail=f"Invalid status: {payload['status']}")
        old_status = cert.status
        cert.status = payload["status"].upper()
        db.commit()

        log_audit_event(
            db=db, action="ADMIN_CERT_STATUS_UPDATE", entity_type="CERTIFICATION",
            entity_id=str(cert_id), user_id=current_user.id,
            details={"old_status": old_status, "new_status": cert.status, "cert_number": cert.certificate_number}
        )

    return {"message": "Certificate updated", "cert_id": cert_id, "status": cert.status}


# ══════════════════════════════════════════════
# 6. EMPLOYMENT MONITORING
# ══════════════════════════════════════════════

@router.get("/employment")
def admin_employment_overview(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    verification_filter: Optional[str] = Query(None, alias="verification"),
    current_user: User = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """Employment monitoring with all statuses from actual records."""
    # Summary counts
    status_counts = db.query(
        EmploymentRecord.status,
        func.count(EmploymentRecord.id)
    ).group_by(EmploymentRecord.status).all()
    status_map = {s or "UNKNOWN": c for s, c in status_counts}

    verification_counts = db.query(
        EmploymentRecord.verification_status,
        func.count(EmploymentRecord.id)
    ).group_by(EmploymentRecord.verification_status).all()
    verify_map = {v or "PENDING": c for v, c in verification_counts}

    salary_stats = db.query(
        func.avg(EmploymentRecord.starting_salary),
        func.avg(EmploymentRecord.current_salary),
        func.min(EmploymentRecord.starting_salary),
        func.max(EmploymentRecord.current_salary)
    ).filter(EmploymentRecord.status == "EMPLOYED").first()

    # Paginated list
    q = db.query(EmploymentRecord)
    if search:
        like = f"%{search}%"
        q = q.filter(or_(
            EmploymentRecord.employer_name.ilike(like),
            EmploymentRecord.job_title.ilike(like)
        ))
    if status_filter and status_filter != "ALL":
        q = q.filter(EmploymentRecord.status == status_filter)
    if verification_filter and verification_filter != "ALL":
        q = q.filter(EmploymentRecord.verification_status == verification_filter)

    total = q.count()
    records = q.order_by(desc(EmploymentRecord.created_at)).offset((page - 1) * per_page).limit(per_page).all()

    rows = []
    for e in records:
        trainee = db.query(Trainee).filter(Trainee.id == e.trainee_id).first()
        t_record = db.query(TrainingRecord).filter(TrainingRecord.trainee_id == e.trainee_id).first()
        rows.append({
            "id": e.id,
            "trainee_id": e.trainee_id,
            "skillpulse_id": trainee.skillpulse_id if trainee else None,
            "trainee_name": trainee.full_name if trainee else None,
            "course_name": t_record.course.course_name if t_record and t_record.course else None,
            "employer_name": e.employer_name,
            "job_title": e.job_title,
            "job_role": e.job_role,
            "industry": e.industry,
            "employment_type": e.employment_type,
            "joining_date": e.joining_date,
            "starting_salary": e.starting_salary,
            "current_salary": e.current_salary,
            "status": e.status,
            "verification_status": e.verification_status,
            "confidence_score": e.confidence_score,
            "created_at": e.created_at.isoformat() if e.created_at else None,
        })

    return {
        "summary": {
            "total_records": total,
            "by_status": {
                "EMPLOYED": status_map.get("EMPLOYED", 0),
                "SEEKING": status_map.get("SEEKING", 0),
                "SELF_EMPLOYED": status_map.get("SELF_EMPLOYED", 0),
                "NOT_SEEKING": status_map.get("NOT_SEEKING", 0),
                "UNKNOWN": status_map.get("UNKNOWN", 0),
            },
            "by_verification": {
                "PENDING": verify_map.get("PENDING", 0),
                "VERIFIED": verify_map.get("VERIFIED", 0),
                "REJECTED": verify_map.get("REJECTED", 0),
            },
            "avg_starting_salary": round(float(salary_stats[0]), 2) if salary_stats and salary_stats[0] else None,
            "avg_current_salary": round(float(salary_stats[1]), 2) if salary_stats and salary_stats[1] else None,
        },
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": max(1, (total + per_page - 1) // per_page),
        "items": rows
    }


# ══════════════════════════════════════════════
# 7. EMPLOYER VERIFICATION QUEUE
# ══════════════════════════════════════════════

@router.get("/employer-verification")
def list_employer_verifications(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: User = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """All employer verifications — pending, verified, rejected."""
    q = db.query(EmployerVerification)
    if status_filter and status_filter != "ALL":
        q = q.filter(EmployerVerification.status == status_filter)

    total = q.count()
    verifications = q.order_by(desc(EmployerVerification.action_timestamp)).offset(
        (page - 1) * per_page
    ).limit(per_page).all()

    rows = []
    for v in verifications:
        emp_record = db.query(EmploymentRecord).filter(EmploymentRecord.id == v.employment_record_id).first()
        trainee = db.query(Trainee).filter(Trainee.id == emp_record.trainee_id).first() if emp_record else None
        employer = db.query(Employer).filter(Employer.id == v.employer_id).first()

        rows.append({
            "id": v.id,
            "employment_record_id": v.employment_record_id,
            "trainee_id": trainee.id if trainee else None,
            "trainee_name": trainee.full_name if trainee else None,
            "skillpulse_id": trainee.skillpulse_id if trainee else None,
            "employer_name": employer.company_name if employer else (emp_record.employer_name if emp_record else None),
            "job_title": v.verified_job_title or (emp_record.job_title if emp_record else None),
            "status": v.status,
            "notes": v.notes,
            "verified_salary": v.verified_salary,
            "verified_joining_date": v.verified_joining_date,
            "confidence_score": v.confidence_score,
            "verification_source": v.verification_source,
            "action_timestamp": v.action_timestamp.isoformat() if v.action_timestamp else None,
        })

    # Summary
    status_counts = db.query(
        EmployerVerification.status, func.count(EmployerVerification.id)
    ).group_by(EmployerVerification.status).all()
    status_map = {s: c for s, c in status_counts}

    return {
        "summary": {
            "PENDING": status_map.get("PENDING", 0),
            "VERIFIED": status_map.get("VERIFIED", 0),
            "REJECTED": status_map.get("REJECTED", 0),
        },
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": max(1, (total + per_page - 1) // per_page),
        "items": rows
    }


@router.patch("/employer-verification/{record_id}")
def admin_update_verification(
    record_id: int,
    payload: Dict[str, Any],
    current_user: User = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """Admin overrides employment verification status."""
    emp_record = db.query(EmploymentRecord).filter(EmploymentRecord.id == record_id).first()
    if not emp_record:
        raise HTTPException(status_code=404, detail="Employment record not found")

    new_status = payload.get("status", "").upper()
    if new_status not in {"VERIFIED", "REJECTED", "PENDING"}:
        raise HTTPException(status_code=400, detail="Invalid verification status")

    old_status = emp_record.verification_status
    emp_record.verification_status = new_status
    if new_status == "VERIFIED":
        emp_record.verified_at = datetime.utcnow()
        emp_record.confidence_score = 1.0

    db.commit()

    log_audit_event(
        db=db, action="ADMIN_VERIFICATION_UPDATE", entity_type="EMPLOYMENT_RECORD",
        entity_id=str(record_id), user_id=current_user.id,
        details={"old_status": old_status, "new_status": new_status, "notes": payload.get("notes")}
    )

    return {"message": "Verification status updated", "record_id": record_id, "status": new_status}


# ══════════════════════════════════════════════
# 8. FOLLOW-UPS
# ══════════════════════════════════════════════

@router.get("/followups")
def admin_followups(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    checkpoint: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    overdue_only: bool = False,
    current_user: User = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """Longitudinal follow-ups with overdue highlighting."""
    today_str = date.today().isoformat()

    q = db.query(Followup)
    if checkpoint and checkpoint != "ALL":
        q = q.filter(Followup.checkpoint == checkpoint)
    if status_filter and status_filter != "ALL":
        q = q.filter(Followup.status == status_filter)
    if overdue_only:
        q = q.filter(
            Followup.status.in_(["SCHEDULED", "SENT"]),
            Followup.scheduled_date <= today_str
        )

    total = q.count()
    followups = q.order_by(asc(Followup.scheduled_date)).offset((page - 1) * per_page).limit(per_page).all()

    rows = []
    for f in followups:
        trainee = db.query(Trainee).filter(Trainee.id == f.trainee_id).first()
        emp = db.query(EmploymentRecord).filter(EmploymentRecord.trainee_id == f.trainee_id).first()

        is_overdue = (
            f.status in ("SCHEDULED", "SENT") and
            f.scheduled_date and
            f.scheduled_date <= today_str
        )

        rows.append({
            "id": f.id,
            "trainee_id": f.trainee_id,
            "trainee_name": trainee.full_name if trainee else None,
            "skillpulse_id": trainee.skillpulse_id if trainee else None,
            "checkpoint": f.checkpoint,
            "status": f.status,
            "scheduled_date": f.scheduled_date,
            "sent_at": f.sent_at.isoformat() if f.sent_at else None,
            "responded_at": f.responded_at.isoformat() if f.responded_at else None,
            "response_data": f.response_data,
            "channel": f.channel,
            "employment_status": emp.status if emp else "NOT_REPORTED",
            "is_overdue": is_overdue,
            "created_at": f.created_at.isoformat() if f.created_at else None,
        })

    # Summary by checkpoint
    checkpoint_counts = db.query(
        Followup.checkpoint, Followup.status, func.count(Followup.id)
    ).group_by(Followup.checkpoint, Followup.status).all()

    summary = {}
    for cp, st, cnt in checkpoint_counts:
        if cp not in summary:
            summary[cp] = {"total": 0, "responded": 0, "scheduled": 0, "overdue": 0}
        summary[cp]["total"] += cnt
        if st == "RESPONDED":
            summary[cp]["responded"] += cnt
        elif st in ("SCHEDULED", "SENT"):
            summary[cp]["scheduled"] += cnt

    total_overdue = db.query(func.count(Followup.id)).filter(
        Followup.status.in_(["SCHEDULED", "SENT"]),
        Followup.scheduled_date <= today_str
    ).scalar() or 0

    return {
        "total": total,
        "total_overdue": total_overdue,
        "page": page,
        "per_page": per_page,
        "pages": max(1, (total + per_page - 1) // per_page),
        "checkpoint_summary": summary,
        "items": rows
    }


# ══════════════════════════════════════════════
# 9. SKILL GAP ANALYTICS
# ══════════════════════════════════════════════

@router.get("/skill-gaps")
def admin_skill_gap_analytics(
    current_user: User = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """Aggregated skill gap analytics from actual trainee records."""
    analyses = db.query(SkillGapAnalysis).all()
    all_skills = db.query(TraineeSkill).all()

    if not analyses and not all_skills:
        return {
            "has_data": False,
            "message": "No sufficient data for skill-gap analysis. Data will appear after trainees complete skill gap assessments.",
            "top_missing_skills": [],
            "top_possessed_skills": [],
            "avg_skill_gap_score": None,
            "avg_job_readiness": None,
            "total_analyzed": 0,
            "total_trainees_with_skills": 0,
        }

    # Missing skills from gap analyses
    missing_counter = Counter()
    matched_counter = Counter()
    for a in analyses:
        for s in (a.missing_skills_json or []):
            missing_counter[s] += 1
        for s in (a.matched_skills_json or []):
            matched_counter[s] += 1

    # Possessed skills from trainee profiles
    possessed_counter = Counter()
    for s in all_skills:
        possessed_counter[s.skill_name] += 1

    avg_gap = round(sum(a.skill_gap_score for a in analyses) / len(analyses), 1) if analyses else None
    avg_readiness = round(sum(a.job_readiness for a in analyses) / len(analyses), 1) if analyses else None

    # Role demand from target_roles in courses
    role_counter = Counter()
    for c in db.query(Course).all():
        for role in (c.target_roles or []):
            role_counter[role] += 1

    # Required skills from courses (demand side)
    skill_demand_counter = Counter()
    for c in db.query(Course).all():
        for sk in (c.required_skills or []):
            skill_demand_counter[sk] += 1

    return {
        "has_data": True,
        "total_analyzed": len(analyses),
        "total_trainees_with_skills": db.query(func.count(func.distinct(TraineeSkill.trainee_id))).scalar() or 0,
        "avg_skill_gap_score": avg_gap,
        "avg_job_readiness": avg_readiness,
        "top_missing_skills": [{"skill": s, "frequency": f} for s, f in missing_counter.most_common(15)],
        "top_possessed_skills": [{"skill": s, "count": c} for s, c in possessed_counter.most_common(15)],
        "skill_demand_from_courses": [{"skill": s, "courses_requiring": c} for s, c in skill_demand_counter.most_common(15)],
        "top_target_roles": [{"role": r, "count": c} for r, c in role_counter.most_common(10)],
    }


# ══════════════════════════════════════════════
# 10. POLICY INSIGHTS — Evidence-Based
# ══════════════════════════════════════════════

@router.get("/policy-insights")
def admin_policy_insights(
    state: Optional[str] = None,
    district: Optional[str] = None,
    provider_id: Optional[int] = None,
    course_id: Optional[int] = None,
    cohort: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """
    Government evidence-based decision support.
    Every insight shows the evidence behind it.
    No fabricated recommendations.
    """
    from app.services.outcome_metrics import dashboard_metrics
    if start_date and end_date and start_date > end_date:
        raise HTTPException(400, "Start date must not follow end date.")

    metrics = dashboard_metrics(db, state, district, provider_id, course_id, cohort, start_date, end_date)
    total_trainees = metrics["total_trainees"]
    employment_rate = metrics["employment_rate_pct"]
    verified_employment = metrics["verified_employment"]
    self_reported = metrics["self_reported_employment"]
    retention_6m = metrics["macro_retention_6m"]

    insights = []
    if total_trainees == 0:
        insights.append({
            "type": "INFO",
            "title": "No data available yet",
            "observation": "No consenting trainee records match the selected filters.",
            "evidence": [],
            "data_quality": "INSUFFICIENT",
        })
    else:
        insights.append({
            "type": "EMPLOYMENT_OUTCOME",
            "title": "Employment Outcome",
            "observation": f"{employment_rate}% of consenting trainees in scope have a current self-reported or verified employment outcome.",
            "evidence": [
                {"label": "Consenting trainees in scope", "value": total_trainees},
                {"label": "Current employed outcomes", "value": metrics["employed_trainees"]},
                {"label": "Employer-verified outcomes", "value": verified_employment},
                {"label": "Self-reported employed outcomes", "value": self_reported},
                {"label": "Verified employment rate", "value": f"{metrics['verified_employment_rate_pct']}%"},
            ],
            "data_quality": "VERIFIED" if verified_employment >= 3 else ("PARTIAL" if metrics["employed_trainees"] else "INSUFFICIENT"),
            "caveat": "Self-reported employment is useful for follow-up workflows but is not treated as employer verification.",
        })

        insights.append({
            "type": "TRAINING_EFFECTIVENESS",
            "title": "Training Effectiveness",
            "observation": f"{metrics['training_completed']} trainees in scope have completed training.",
            "evidence": [
                {"label": "Training completed", "value": metrics["training_completed"]},
                {"label": "Certificates issued", "value": metrics["certificates_uploaded"]},
                {"label": "Certificate issuance rate", "value": f"{metrics['certificate_issuance_rate_pct']}%"},
                {"label": "Certified-to-employed conversion", "value": f"{metrics['placement_conversion_rate']}%"},
            ],
            "data_quality": "PARTIAL" if metrics["training_completed"] else "INSUFFICIENT",
            "caveat": "Completion and certification are observed records only; missing provider uploads are not imputed.",
        })

        if retention_6m is not None:
            insights.append({
                "type": "RETENTION",
                "title": "6-Month Retention",
                "observation": f"{retention_6m}% of 6-month follow-up respondents reported being employed.",
                "evidence": [
                    {"label": "6-month responses", "value": metrics["retention"]["6_MONTHS"]["responses"]},
                    {"label": "Self-reported employed at 6 months", "value": metrics["retention"]["6_MONTHS"]["employed"]},
                    {"label": "Verified retained outcomes", "value": metrics["retention"]["6_MONTHS"]["verified"]},
                ],
                "data_quality": "PARTIAL",
                "caveat": "This is follow-up response retention, not proof of continuous same-employer tenure.",
            })

    return {
        "generated_at": datetime.utcnow().isoformat(),
        "data_disclaimer": metrics["data_note"],
        "active_filters": metrics["active_filters"],
        "summary_metrics": {
            "total_trainees": total_trainees,
            "employment_rate_pct": employment_rate,
            "verified_employment_rate_pct": metrics["verified_employment_rate_pct"],
            "avg_wage_growth_pct": metrics["avg_wage_growth_pct"],
            "retention_6m_pct": retention_6m,
            "verified_employment_count": verified_employment,
            "self_reported_employment_count": self_reported,
        },
        "insights": insights,
        "course_performance": metrics["course_employment_stats"],
        "district_performance": metrics["districts_data"],
        "data_trust": metrics["data_trust"],
        "ai_status": metrics["ai_status"],
    }

# 11. REPORTS — Filtered + CSV Export
# ══════════════════════════════════════════════

@router.get("/reports")
def generate_report(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    state: Optional[str] = None,
    district: Optional[str] = None,
    course_id: Optional[int] = None,
    provider_id: Optional[int] = None,
    employment_status: Optional[str] = None,
    format: str = Query("json", pattern="^(json|csv)$"),
    current_user: User = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """Filtered report generation with optional CSV export."""
    log_audit_event(
        db=db, action="ADMIN_REPORT_GENERATED", entity_type="REPORT",
        entity_id=None, user_id=current_user.id,
        details={
            "filters": {
                "date_from": date_from, "date_to": date_to,
                "state": state, "district": district,
                "course_id": course_id, "provider_id": provider_id,
                "employment_status": employment_status
            },
            "format": format
        }
    )

    q = db.query(Trainee)
    if state and state != "ALL":
        q = q.filter(Trainee.state == state)
    if district and district != "ALL":
        q = q.filter(Trainee.district == district)
    if date_from:
        try:
            q = q.filter(Trainee.created_at >= datetime.strptime(date_from, "%Y-%m-%d"))
        except ValueError:
            pass
    if date_to:
        try:
            q = q.filter(Trainee.created_at <= datetime.strptime(date_to, "%Y-%m-%d"))
        except ValueError:
            pass

    trainees = q.all()
    trainee_ids = [t.id for t in trainees]

    # Apply course/provider filter via training records
    if course_id and trainee_ids:
        filtered_ids = [r.trainee_id for r in db.query(TrainingRecord.trainee_id).filter(
            TrainingRecord.trainee_id.in_(trainee_ids),
            TrainingRecord.course_id == course_id
        ).all()]
        trainee_ids = filtered_ids
        trainees = [t for t in trainees if t.id in set(trainee_ids)]

    if provider_id and trainee_ids:
        filtered_ids = [r.trainee_id for r in db.query(TrainingRecord.trainee_id).filter(
            TrainingRecord.trainee_id.in_(trainee_ids),
            TrainingRecord.provider_id == provider_id
        ).all()]
        trainee_ids = filtered_ids
        trainees = [t for t in trainees if t.id in set(trainee_ids)]

    # Build rows (NO sensitive personal data beyond needed for report)
    rows = []
    for t in trainees:
        t_record = db.query(TrainingRecord).filter(TrainingRecord.trainee_id == t.id).first()
        cert = db.query(Certification).filter(Certification.trainee_id == t.id).first()
        emp = db.query(EmploymentRecord).filter(EmploymentRecord.trainee_id == t.id).first()

        if employment_status and employment_status != "ALL":
            emp_stat = emp.status if emp else "NOT_REPORTED"
            if emp_stat != employment_status:
                continue

        rows.append({
            "skillpulse_id": t.skillpulse_id,
            "state": t.state or "",
            "district": t.district or "",
            "gender": t.gender or "",
            "education": t.education or "",
            "course_name": t_record.course.course_name if t_record and t_record.course else "",
            "provider_name": t_record.provider.organization_name if t_record and t_record.provider else "",
            "training_status": t_record.completion_status if t_record else "NOT_STARTED",
            "certificate_status": cert.status if cert else "NOT_ISSUED",
            "employment_status": emp.status if emp else "NOT_REPORTED",
            "employer_name": emp.employer_name if emp else "",
            "job_title": emp.job_title if emp else "",
            "joining_date": emp.joining_date if emp else "",
            "verification_status": emp.verification_status if emp else "",
            "registered_at": t.created_at.strftime("%Y-%m-%d") if t.created_at else "",
        })

    total_employed_in_report = sum(1 for r in rows if r["employment_status"] == "EMPLOYED")
    total_completed_in_report = sum(1 for r in rows if r["training_status"] == "COMPLETED")

    if format == "csv":
        output = io.StringIO()
        if rows:
            writer = csv.DictWriter(output, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        else:
            output.write("No records match the selected filters.\n")

        output.seek(0)
        filename = f"skillpulse_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    return {
        "generated_at": datetime.utcnow().isoformat(),
        "generated_by": current_user.full_name,
        "filters_applied": {
            "date_from": date_from or "All time",
            "date_to": date_to or "All time",
            "state": state or "All",
            "district": district or "All",
            "course_id": course_id,
            "provider_id": provider_id,
            "employment_status": employment_status or "All",
        },
        "total_records": len(rows),
        "summary": {
            "total_trainees": len(rows),
            "employed": total_employed_in_report,
            "training_completed": total_completed_in_report,
            "employment_rate_pct": round((total_employed_in_report / max(len(rows), 1)) * 100.0, 1) if rows else 0.0,
            "completion_rate_pct": round((total_completed_in_report / max(len(rows), 1)) * 100.0, 1) if rows else 0.0,
        },
        "records": rows
    }


# ══════════════════════════════════════════════
# 12. AUDIT LOGS
# ══════════════════════════════════════════════

@router.get("/audit-logs")
def list_audit_logs(
    page: int = Query(1, ge=1),
    per_page: int = Query(30, ge=1, le=100),
    action: Optional[str] = None,
    entity_type: Optional[str] = None,
    user_id_filter: Optional[int] = Query(None, alias="user_id"),
    current_user: User = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """Paginated audit log viewer."""
    q = db.query(AuditLog)
    if action:
        q = q.filter(AuditLog.action.ilike(f"%{action}%"))
    if entity_type:
        q = q.filter(AuditLog.entity_type == entity_type)
    if user_id_filter:
        q = q.filter(AuditLog.user_id == user_id_filter)

    total = q.count()
    logs = q.order_by(desc(AuditLog.created_at)).offset((page - 1) * per_page).limit(per_page).all()

    rows = []
    for log in logs:
        actor = db.query(User.full_name, User.email, User.role).filter(User.id == log.user_id).first() if log.user_id else None
        rows.append({
            "id": log.id,
            "user_id": log.user_id,
            "actor_name": actor[0] if actor else "System",
            "actor_email": actor[1] if actor else None,
            "actor_role": actor[2] if actor else None,
            "action": log.action,
            "entity_type": log.entity_type,
            "entity_id": log.entity_id,
            "details": log.details_json,
            "timestamp": log.created_at.isoformat() if log.created_at else None,
        })

    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": max(1, (total + per_page - 1) // per_page),
        "items": rows
    }


# ══════════════════════════════════════════════
# 13. SETTINGS — Admin Info
# ══════════════════════════════════════════════

@router.get("/settings")
def admin_settings(
    current_user: User = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """Admin profile and platform configuration info."""
    total_admins = db.query(func.count(User.id)).filter(User.role == "ADMIN").scalar() or 0
    total_users = db.query(func.count(User.id)).scalar() or 0

    return {
        "admin_profile": {
            "id": current_user.id,
            "full_name": current_user.full_name,
            "email": current_user.email,
            "role": current_user.role,
            "is_active": current_user.is_active,
            "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
        },
        "platform_info": {
            "total_admin_accounts": total_admins,
            "total_registered_users": total_users,
        }
    }

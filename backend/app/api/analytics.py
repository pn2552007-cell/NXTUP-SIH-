from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, case

from app.database import get_db
from app.models.models import (
    Trainee, Provider, Course, TrainingRecord, Assessment,
    Certification, EmploymentRecord, Followup, WageHistory, SkillGapAnalysis
)
from app.schemas.schemas import (
    AnalyticsOverviewResponse, DistrictMetric, ProviderMetric, CourseMetric
)
from app.auth.jwt_handler import get_current_user

router = APIRouter(prefix="/analytics", tags=["Longitudinal Analytics"])

@router.get("/overview", response_model=AnalyticsOverviewResponse)
def get_analytics_overview(
    state: Optional[str] = None,
    district: Optional[str] = None,
    provider_id: Optional[int] = None,
    course_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Macro overview computed dynamically with SQL aggregation.
    Zero-data safe: returns 0 values and clear empty state indicators.
    """
    trainee_q = db.query(func.count(Trainee.id))
    if state and state != "ALL":
        trainee_q = trainee_q.filter(Trainee.state == state)
    if district and district != "ALL":
        trainee_q = trainee_q.filter(Trainee.district == district)

    total_trainees = trainee_q.scalar() or 0
    total_courses = db.query(func.count(Course.id)).scalar() or 0
    total_providers = db.query(func.count(Provider.id)).scalar() or 0
    total_employers = db.query(func.count(func.distinct(EmploymentRecord.employer_name))).scalar() or 0
    total_certified = db.query(func.count(Certification.id)).scalar() or 0

    # Employment count
    emp_q = db.query(func.count(EmploymentRecord.id)).filter(EmploymentRecord.status == "EMPLOYED")
    total_employed = emp_q.scalar() or 0

    employment_rate_pct = round((total_employed / max(total_trainees, 1)) * 100.0, 1) if total_trainees > 0 else 0.0
    certification_rate_pct = round((total_certified / max(total_trainees, 1)) * 100.0, 1) if total_trainees > 0 else 0.0

    # Retention at 6m and 12m from actual followups
    fup_6m_total = db.query(func.count(Followup.id)).filter(Followup.checkpoint == "6_MONTHS").scalar() or 0
    fup_6m_employed = db.query(func.count(Followup.id)).filter(
        Followup.checkpoint == "6_MONTHS",
        Followup.status == "RESPONDED"
    ).scalar() or 0

    retention_6m_pct = None
    retention_status = "Insufficient data"
    if fup_6m_total >= 3 and total_employed > 0:
        retention_6m_pct = round((fup_6m_employed / fup_6m_total) * 100.0, 1)
        retention_status = f"{retention_6m_pct}% verified at 6 months"

    # Wage growth calculation from actual wage history records
    avg_growth = db.query(func.avg(WageHistory.growth_pct_since_starting)).filter(
        WageHistory.growth_pct_since_starting > 0
    ).scalar()
    
    avg_wage_growth_pct = round(float(avg_growth), 1) if avg_growth is not None else None
    wage_growth_status = f"{avg_wage_growth_pct}% avg growth" if avg_wage_growth_pct is not None else "No wage history available"

    return AnalyticsOverviewResponse(
        total_trainees=total_trainees,
        total_courses=total_courses,
        total_providers=total_providers,
        total_employers=total_employers,
        total_certified=total_certified,
        total_employed=total_employed,
        employment_rate_pct=employment_rate_pct,
        certification_rate_pct=certification_rate_pct,
        retention_rate_6m_pct=retention_6m_pct,
        retention_rate_12m_pct=None,
        retention_status=retention_status,
        avg_wage_growth_pct=avg_wage_growth_pct,
        wage_growth_status=wage_growth_status,
        median_time_to_employment_days=None
    )

@router.get("/employment")
def get_employment_analytics(db: Session = Depends(get_db)):
    """Breakdown of employment outcomes by type and status."""
    status_counts = db.query(
        EmploymentRecord.status,
        func.count(EmploymentRecord.id)
    ).group_by(EmploymentRecord.status).all()

    type_counts = db.query(
        EmploymentRecord.employment_type,
        func.count(EmploymentRecord.id)
    ).filter(EmploymentRecord.status == "EMPLOYED").group_by(EmploymentRecord.employment_type).all()

    salaries = db.query(
        func.avg(EmploymentRecord.starting_salary),
        func.avg(EmploymentRecord.current_salary)
    ).filter(EmploymentRecord.status == "EMPLOYED").first()

    return {
        "status_distribution": {s or "UNKNOWN": c for s, c in status_counts},
        "employment_type_distribution": {t or "FULL_TIME": c for t, c in type_counts},
        "avg_starting_salary": round(float(salaries[0]), 2) if salaries and salaries[0] else None,
        "avg_current_salary": round(float(salaries[1]), 2) if salaries and salaries[1] else None
    }

@router.get("/retention")
def get_retention_analytics(db: Session = Depends(get_db)):
    """Calculates 6-month and 12-month retention rates from actual longitudinal records."""
    fups = db.query(
        Followup.checkpoint,
        func.count(Followup.id).label("total"),
        func.sum(case((Followup.status == "RESPONDED", 1), else_=0)).label("responded")
    ).group_by(Followup.checkpoint).all()

    retention_by_checkpoint = {}
    for cp, total, responded in fups:
        rate = round((responded / total) * 100.0, 1) if total > 0 else 0.0
        retention_by_checkpoint[cp] = {
            "total_scheduled": total,
            "retained_count": responded or 0,
            "retention_rate_pct": rate if total >= 3 else None,
            "status": "Verified" if total >= 3 else "Insufficient data"
        }

    return {
        "checkpoints": retention_by_checkpoint,
        "summary": "Retention calculated strictly from verified follow-up responses." if fups else "Insufficient data"
    }

@router.get("/wage-growth")
def get_wage_growth_analytics(db: Session = Depends(get_db)):
    """Computes wage growth distributions across all cohorts."""
    wages = db.query(WageHistory).filter(WageHistory.growth_pct_since_starting > 0).all()
    if not wages:
        return {
            "has_data": False,
            "avg_growth_pct": None,
            "count": 0,
            "message": "No wage history available."
        }

    growth_values = [w.growth_pct_since_starting for w in wages]
    avg_growth = round(sum(growth_values) / len(growth_values), 1)

    return {
        "has_data": True,
        "avg_growth_pct": avg_growth,
        "count": len(growth_values),
        "min_growth_pct": min(growth_values),
        "max_growth_pct": max(growth_values)
    }

@router.get("/skill-gaps")
def get_skill_gaps_analytics(db: Session = Depends(get_db)):
    """Aggregates industry skill gaps identified across trainees."""
    analyses = db.query(SkillGapAnalysis).all()
    if not analyses:
        return {
            "has_data": False,
            "avg_skill_gap_score": None,
            "top_missing_skills": [],
            "message": "No skill-gap analysis available yet."
        }

    from collections import Counter
    missing_counter = Counter()
    for a in analyses:
        for s in (a.missing_skills_json or []):
            missing_counter[s] += 1

    avg_gap = round(sum(a.skill_gap_score for a in analyses) / len(analyses), 1)

    return {
        "has_data": True,
        "avg_skill_gap_score": avg_gap,
        "total_analyzed": len(analyses),
        "top_missing_skills": [{"skill": s, "frequency": f} for s, f in missing_counter.most_common(10)]
    }

@router.get("/providers")
def get_providers_analytics(db: Session = Depends(get_db)):
    """Provider performance metrics computed purely from SQL joins."""
    providers = db.query(Provider).all()
    metrics = []
    for p in providers:
        total_trained = db.query(func.count(TrainingRecord.id)).filter(TrainingRecord.provider_id == p.id).scalar() or 0
        t_ids = [r.trainee_id for r in db.query(TrainingRecord.trainee_id).filter(TrainingRecord.provider_id == p.id).all()]
        certified = db.query(func.count(Certification.id)).filter(Certification.trainee_id.in_(t_ids)).scalar() if t_ids else 0
        employed = db.query(func.count(EmploymentRecord.id)).filter(
            EmploymentRecord.trainee_id.in_(t_ids),
            EmploymentRecord.status == "EMPLOYED"
        ).scalar() if t_ids else 0

        emp_rate = round((employed / max(total_trained, 1)) * 100.0, 1) if total_trained > 0 else 0.0

        metrics.append({
            "provider_id": p.id,
            "organization_name": p.organization_name,
            "state": p.state,
            "total_trained": total_trained,
            "certified": certified,
            "employed": employed,
            "employment_rate_pct": emp_rate
        })
    return metrics

@router.get("/courses")
def get_courses_analytics(db: Session = Depends(get_db)):
    """Course outcome benchmarks from SQL aggregation."""
    courses = db.query(Course).all()
    metrics = []
    for c in courses:
        total_enrolled = db.query(func.count(TrainingRecord.id)).filter(TrainingRecord.course_id == c.id).scalar() or 0
        completed = db.query(func.count(TrainingRecord.id)).filter(
            TrainingRecord.course_id == c.id,
            TrainingRecord.completion_status == "COMPLETED"
        ).scalar() or 0
        t_ids = [r.trainee_id for r in db.query(TrainingRecord.trainee_id).filter(TrainingRecord.course_id == c.id).all()]
        employed = db.query(func.count(EmploymentRecord.id)).filter(
            EmploymentRecord.trainee_id.in_(t_ids),
            EmploymentRecord.status == "EMPLOYED"
        ).scalar() if t_ids else 0

        emp_rate = round((employed / max(total_enrolled, 1)) * 100.0, 1) if total_enrolled > 0 else 0.0

        metrics.append({
            "course_id": c.id,
            "course_name": c.course_name,
            "domain": c.domain,
            "total_enrolled": total_enrolled,
            "completed": completed,
            "employed": employed,
            "employment_rate_pct": emp_rate
        })
    return metrics

@router.get("/districts")
def get_districts_analytics(db: Session = Depends(get_db)):
    """Geographic district aggregation for policy analysis."""
    districts = db.query(
        Trainee.district,
        Trainee.state,
        func.count(Trainee.id).label("total")
    ).filter(Trainee.district.isnot(None)).group_by(Trainee.district, Trainee.state).all()

    results = []
    for dist, st, total in districts:
        t_ids = [t.id for t in db.query(Trainee.id).filter(Trainee.district == dist).all()]
        employed = db.query(func.count(EmploymentRecord.id)).filter(
            EmploymentRecord.trainee_id.in_(t_ids),
            EmploymentRecord.status == "EMPLOYED"
        ).scalar() if t_ids else 0

        emp_rate = round((employed / max(total, 1)) * 100.0, 1) if total > 0 else 0.0

        results.append({
            "district": dist,
            "state": st or "Unspecified",
            "trainees": total,
            "employed": employed,
            "employment_rate_pct": emp_rate
        })
    return results

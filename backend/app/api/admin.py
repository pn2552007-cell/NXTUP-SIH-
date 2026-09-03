from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.models import (
    User, Trainee, Provider, Employer, Course, TrainingRecord,
    Assessment, Certification, EmploymentRecord, SkillGapAnalysis, Followup, WageHistory
)
from app.auth.jwt_handler import get_current_user, require_role

router = APIRouter(prefix="/admin", tags=["Government & Admin Policy Analytics"])

@router.get("/dashboard")
def get_admin_dashboard(
    state: Optional[str] = None,
    district: Optional[str] = None,
    provider_id: Optional[int] = None,
    course_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    # Trainees count
    trainee_query = db.query(Trainee)
    if state and state != "ALL":
        trainee_query = trainee_query.filter(Trainee.state == state)
    if district and district != "ALL":
        trainee_query = trainee_query.filter(Trainee.district == district)

    total_trainees = trainee_query.count()
    total_providers = db.query(Provider).count()
    total_courses = db.query(Course).count()
    total_employers = db.query(Employer).count()

    # Macro rates
    emp_records = db.query(EmploymentRecord).filter(EmploymentRecord.status == "EMPLOYED").all()
    employed_count = len(emp_records)
    macro_emp_rate = round((employed_count / max(total_trainees, 1)) * 100.0, 1) if total_trainees > 0 else 0.0

    certs_count = db.query(Certification).count()
    placement_conversion = round((employed_count / max(certs_count, 1)) * 100.0, 1) if certs_count > 0 else 0.0

    # Wage growth calculation across all trainees with wage history
    growth_records = db.query(WageHistory.growth_pct_since_starting).filter(
        WageHistory.growth_pct_since_starting > 0
    ).all()
    growth_rates = [w[0] for w in growth_records]
    avg_wage_growth = round(sum(growth_rates) / len(growth_rates), 1) if growth_rates else None

    # Retention rates from actual 6m and 12m follow-ups
    fup_6m_total = db.query(Followup).filter(Followup.checkpoint == "6_MONTHS").count()
    fup_6m_responded = db.query(Followup).filter(
        Followup.checkpoint == "6_MONTHS",
        Followup.status == "RESPONDED"
    ).count()
    macro_retention_6m = round((fup_6m_responded / fup_6m_total) * 100.0, 1) if fup_6m_total >= 3 else None

    # Skill gap index from actual records
    gaps = db.query(SkillGapAnalysis.skill_gap_score).all()
    gap_scores = [g[0] for g in gaps]
    macro_gap_index = round(sum(gap_scores) / len(gap_scores), 1) if gap_scores else None

    # District Trends Data from database
    district_rows = db.query(
        Trainee.district,
        Trainee.state,
        func.count(Trainee.id).label("total")
    ).filter(Trainee.district.isnot(None)).group_by(Trainee.district, Trainee.state).all()

    district_data = []
    for d_name, s_name, d_total in district_rows:
        t_ids = [t.id for t in db.query(Trainee.id).filter(Trainee.district == d_name).all()]
        d_emp = db.query(EmploymentRecord).filter(
            EmploymentRecord.trainee_id.in_(t_ids),
            EmploymentRecord.status == "EMPLOYED"
        ).count() if t_ids else 0
        d_rate = round((d_emp / max(d_total, 1)) * 100.0, 1) if d_total > 0 else 0.0

        district_data.append({
            "district": d_name,
            "state": s_name or "Unspecified",
            "total_trainees": d_total,
            "employment_rate": d_rate,
            "retention_rate": None,
            "avg_wage_growth": None
        })

    # Provider Rankings from database
    providers = db.query(Provider).all()
    provider_rankings = []
    for p in providers:
        p_recs = db.query(TrainingRecord).filter(TrainingRecord.provider_id == p.id).all()
        p_total = len(p_recs)
        p_t_ids = [r.trainee_id for r in p_recs]
        p_certs = db.query(Certification).filter(Certification.trainee_id.in_(p_t_ids)).count() if p_t_ids else 0
        p_emps = db.query(EmploymentRecord).filter(
            EmploymentRecord.trainee_id.in_(p_t_ids),
            EmploymentRecord.status == "EMPLOYED"
        ).all() if p_t_ids else []

        p_cert_pct = round((p_certs / max(p_total, 1)) * 100.0, 1) if p_total > 0 else 0.0
        p_emp_pct = round((len(p_emps) / max(p_total, 1)) * 100.0, 1) if p_total > 0 else 0.0
        p_salaries = [e.current_salary for e in p_emps if e.current_salary is not None]
        p_avg_sal = round(sum(p_salaries) / len(p_salaries), 2) if p_salaries else None

        impact_score = round((p_cert_pct * 0.4) + (p_emp_pct * 0.6), 1) if p_total > 0 else 0.0

        provider_rankings.append({
            "provider_id": p.id,
            "provider_name": p.organization_name,
            "state": p.state or "Unspecified",
            "total_trained": p_total,
            "certified_pct": p_cert_pct,
            "employed_pct": p_emp_pct,
            "retention_6m_pct": None,
            "avg_salary": p_avg_sal,
            "impact_score": impact_score
        })

    # Domain breakdown from database
    domains = db.query(
        Course.domain,
        func.count(Course.id)
    ).group_by(Course.domain).all()

    domain_data = []
    for dom_name, c_cnt in domains:
        c_ids = [c.id for c in db.query(Course.id).filter(Course.domain == dom_name).all()]
        t_recs = db.query(TrainingRecord).filter(TrainingRecord.course_id.in_(c_ids)).all() if c_ids else []
        t_ids = [r.trainee_id for r in t_recs]
        emp_cnt = db.query(EmploymentRecord).filter(
            EmploymentRecord.trainee_id.in_(t_ids),
            EmploymentRecord.status == "EMPLOYED"
        ).count() if t_ids else 0
        emp_rate = round((emp_cnt / max(len(t_recs), 1)) * 100.0, 1) if t_recs else 0.0

        domain_data.append({
            "domain": dom_name,
            "trainees": len(t_recs),
            "employment_rate": emp_rate,
            "growth_pct": None
        })

    return {
        "total_trainees": total_trainees,
        "total_providers": total_providers,
        "total_courses": total_courses,
        "total_employers": total_employers,
        "macro_employment_rate": macro_emp_rate,
        "placement_conversion_rate": placement_conversion,
        "avg_wage_growth_pct": avg_wage_growth,
        "macro_retention_6m": macro_retention_6m,
        "macro_retention_12m": None,
        "macro_skill_gap_index": macro_gap_index,
        "districts_data": district_data,
        "provider_rankings": provider_rankings,
        "domains_breakdown": domain_data,
        "active_filters": {"state": state or "ALL", "district": district or "ALL"}
    }

@router.get("/filters")
def get_available_filters(db: Session = Depends(get_db)):
    states = [s[0] for s in db.query(Trainee.state).distinct().filter(Trainee.state.isnot(None)).all()]
    districts = [d[0] for d in db.query(Trainee.district).distinct().filter(Trainee.district.isnot(None)).all()]
    providers = [{"id": p.id, "name": p.organization_name} for p in db.query(Provider).all()]
    courses = [{"id": c.id, "name": c.course_name, "domain": c.domain} for c in db.query(Course).all()]

    return {
        "states": ["ALL"] + states,
        "districts": ["ALL"] + districts,
        "providers": providers,
        "courses": courses
    }

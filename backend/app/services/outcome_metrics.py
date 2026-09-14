"""Scoped, distinct-trainee metrics. Missing observations are never invented."""
from collections import Counter, defaultdict
from app.models.models import (
    Trainee, TrainingRecord, EmploymentRecord, Certification, Followup,
    SkillGapAnalysis, Provider, Course, Employer, User, Intervention, Outcome,
)


def dashboard_metrics(db, state=None, district=None, provider_id=None, course_id=None,
                      cohort=None, start_date=None, end_date=None):
    query = db.query(Trainee).filter(Trainee.consent_given == True)
    if state and state != "ALL":
        query = query.filter(Trainee.state == state)
    if district and district != "ALL":
        query = query.filter(Trainee.district == district)
    training = db.query(TrainingRecord)
    for field, value in [(TrainingRecord.provider_id, provider_id), (TrainingRecord.course_id, course_id),
                         (TrainingRecord.cohort_id, cohort if cohort != "ALL" else None)]:
        if value:
            training = training.filter(field == value)
    # Period refers to training completion/end date, not account creation.
    if start_date:
        training = training.filter(TrainingRecord.end_date >= str(start_date))
    if end_date:
        training = training.filter(TrainingRecord.end_date <= str(end_date))
    if any([provider_id, course_id, cohort and cohort != "ALL", start_date, end_date]):
        query = query.filter(Trainee.id.in_(training.with_entities(TrainingRecord.trainee_id)))
    trainees = query.all()
    ids = {t.id for t in trainees}
    records = training.filter(TrainingRecord.trainee_id.in_(ids)).all()
    employment = db.query(EmploymentRecord).filter(EmploymentRecord.trainee_id.in_(ids)).order_by(EmploymentRecord.created_at, EmploymentRecord.id).all()
    latest = {e.trainee_id: e for e in employment}
    employed = {i for i, e in latest.items() if e.status == "EMPLOYED"}
    outcomes = db.query(Outcome).filter(Outcome.trainee_id.in_(ids)).order_by(Outcome.created_at, Outcome.id).all()
    latest_outcomes = {o.trainee_id: o for o in outcomes}
    verified_from_outcomes = {
        i for i, o in latest_outcomes.items()
        if i in employed and o.placement_status == 1 and o.is_verified
    }
    verified = {
        i for i in employed
        if i in verified_from_outcomes or latest[i].verification_status == "VERIFIED"
    }
    certs = db.query(Certification).filter(Certification.trainee_id.in_(ids), Certification.status == "ISSUED").all()
    certified = {c.trainee_id for c in certs if not course_id or c.course_id == course_id}
    followups = db.query(Followup).filter(Followup.trainee_id.in_(ids)).all()
    gaps = db.query(SkillGapAnalysis).filter(SkillGapAnalysis.trainee_id.in_(ids)).order_by(SkillGapAnalysis.created_at, SkillGapAnalysis.id).all()
    latest_gaps = list({g.trainee_id: g for g in gaps}.values())
    def pct(n, d):
        return round(100 * n / d, 1) if d else 0.0
    def comparison(member_ids):
        member_ids = set(member_ids)
        employed_count = len(member_ids & employed)
        verified_count = len(member_ids & verified)
        return {"total": len(member_ids), "employed": len(member_ids & employed),
                "verified": verified_count,
                "self_reported": max(0, employed_count - verified_count),
                "rate": pct(employed_count, len(member_ids)),
                "verified_rate": pct(verified_count, len(member_ids))}
    district_groups = defaultdict(set)
    for t in trainees:
        district_groups[(t.district or "Unspecified", t.state or "Unspecified")].add(t.id)
    districts = []
    for (d, s), members in district_groups.items():
        m = comparison(members)
        districts.append({"district": d, "state": s, "total_trainees": m["total"],
                          "employment_rate": m["rate"], "verified_count": m["verified"],
                          "self_reported_count": m["self_reported"],
                          "verified_employment_rate": m["verified_rate"]})
    providers = []
    for p in db.query(Provider).all():
        members = {r.trainee_id for r in records if r.provider_id == p.id}
        if not members:
            continue
        m = comparison(members)
        impact_score = round((m["verified_rate"] * 0.7) + (m["rate"] * 0.3), 1)
        providers.append({"provider_id": p.id, "provider_name": p.organization_name, "state": p.state,
                          "total_trained": m["total"], "employed_pct": m["rate"],
                          "verified_count": m["verified"], "self_reported_count": m["self_reported"],
                          "verified_employment_rate": m["verified_rate"],
                          "impact_score": impact_score})
    courses = []
    domains = defaultdict(set)
    for c in db.query(Course).all():
        members = {r.trainee_id for r in records if r.course_id == c.id}
        if not members:
            continue
        m = comparison(members)
        courses.append({"course": c.course_name, "domain": c.domain, "enrolled": m["total"],
                        "employed": m["employed"], "verified": m["verified"],
                        "self_reported": m["self_reported"], "rate": m["rate"],
                        "verified_employment_rate": m["verified_rate"]})
        domains[c.domain].update(members)
    retention = {}
    for cp in ("30_DAYS", "90_DAYS", "6_MONTHS", "12_MONTHS"):
        responses = [f for f in followups if f.checkpoint == cp and f.status == "RESPONDED" and isinstance((f.response_data or {}).get("employed"), bool)]
        retained = [f for f in responses if f.response_data["employed"]]
        verified_retained = [
            o for o in latest_outcomes.values()
            if o.is_verified and (
                (cp == "6_MONTHS" and o.retention_status_6m == 1) or
                (cp == "12_MONTHS" and o.retention_status_12m == 1)
            )
        ]
        retention[cp] = {"responses": len(responses), "employed": len(retained),
                         "verified": len(verified_retained) if cp in ("6_MONTHS", "12_MONTHS") else 0,
                         "rate": pct(len(retained), len(responses)) if responses else None}
    growth = [100 * (e.current_salary - e.starting_salary) / e.starting_salary
              for e in latest.values() if e.status == "EMPLOYED" and e.starting_salary and e.starting_salary > 0 and e.current_salary is not None]
    missing = Counter(s for g in latest_gaps for s in (g.missing_skills_json or []) if isinstance(s, str))
    reasons = Counter(e.non_placement_reason for e in latest.values() if e.status != "EMPLOYED" and e.non_placement_reason)
    interventions = Counter(i.status for i in db.query(Intervention).filter(Intervention.trainee_id.in_(ids)))
    self_reported_employed = sum(e.status == "EMPLOYED" and e.verification_status != "VERIFIED" for e in latest.values())
    return {
        "total_users": db.query(User).count(), "total_trainees": len(ids),
        "total_providers": len(providers), "total_courses": len(courses), "total_employers": db.query(Employer).count(),
        "employed_trainees": len(employed), "verified_employment": len(verified),
        "verified_outcome_records": len(verified_from_outcomes),
        "self_reported_pending": self_reported_employed,
        "self_reported_employment": self_reported_employed,
        "seeking_employment": sum(e.status == "SEEKING" for e in latest.values()),
        "unemployed_trainees": len(ids - employed), "self_employed": sum(e.status == "SELF_EMPLOYED" for e in latest.values()),
        "training_completed": len({r.trainee_id for r in records if r.completion_status == "COMPLETED"}),
        "certificates_uploaded": len(certs), "certificates_pending_verification": 0,
        "pending_followups": sum(f.status in ("SCHEDULED", "SENT") for f in followups),
        "employment_rate_pct": pct(len(employed), len(ids)), "macro_employment_rate": pct(len(employed), len(ids)),
        "verified_employment_rate_pct": pct(len(verified), len(ids)),
        "certificate_issuance_rate_pct": pct(len(certified), len(ids)),
        "placement_conversion_rate": pct(len(certified & employed), len(certified)),
        "macro_retention_6m": retention["6_MONTHS"]["rate"], "retention": retention,
        "macro_skill_gap_index": round(sum(g.skill_gap_score for g in latest_gaps) / len(latest_gaps), 1) if latest_gaps else None,
        "avg_wage_growth_pct": round(sum(growth) / len(growth), 1) if growth else None,
        "wage_observations": len(growth), "course_employment_stats": courses,
        "domains_breakdown": [{"domain": d, "trainees": len(m), "employment_rate": comparison(m)["rate"]} for d, m in domains.items()],
        "districts_data": districts, "provider_rankings": providers,
        "non_placement_reasons": dict(reasons), "missing_skills": dict(missing), "interventions": dict(interventions),
        "data_trust": {
            "label": "Live database records",
            "employment_basis": "Self-reported employment is counted separately from employer-verified outcomes.",
            "retention_basis": "Retention uses trainee follow-up responses; verified retention is shown only when verified outcome records exist.",
            "ml_status": "Placement Risk Model is PLANNED until trained and evaluated on real verified pilot outcomes.",
        },
        "ai_status": {
            "placement_risk_model": {
                "status": "PLANNED",
                "available": False,
                "disclaimer": "Prototype only. No accuracy, risk score, or placement probability is claimed from synthetic/demo data.",
            },
            "skill_gap_analysis": {
                "status": "LIVE",
                "basis": "Rule/AI-assisted competency matching from trainee skills and target role requirements.",
            },
        },
        "data_note": "Consenting trainees only. Employment and wage figures include self-reports; employer-verified counts are separate. Retention is employment among checkpoint respondents, not proof of continuous same-employer tenure.",
        "active_filters": {"state": state, "district": district, "provider_id": provider_id, "course_id": course_id, "cohort": cohort, "start_date": start_date, "end_date": end_date},
    }

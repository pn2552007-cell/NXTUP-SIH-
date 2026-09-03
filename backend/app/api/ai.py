from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import (
    User, Trainee, TraineeSkill, Assessment, Certification,
    TrainingRecord, Course, SkillGapAnalysis
)
from app.schemas.schemas import SkillGapRequest, SkillGapResponse
from app.ai.ai_service import AIService
from app.ai.skill_gap_engine import JOB_PROFILES
from app.auth.jwt_handler import get_current_user
from app.utils.audit import log_audit_event

router = APIRouter(prefix="/ai", tags=["AI Skill Gap & Role Analytics"])

ai_service = AIService()

@router.get("/job-roles")
def get_supported_job_roles():
    roles = []
    for role_name, data in JOB_PROFILES.items():
        roles.append({
            "title": role_name,
            "core_skills": list(data["core_skills"].keys()),
            "advanced_skills": list(data["advanced_skills"].keys()),
            "recommended_courses": data.get("recommended_courses", [])
        })
    return roles

@router.post("/skill-gap", response_model=SkillGapResponse)
def analyze_skill_gap(
    request: SkillGapRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    trainee_skills = request.trainee_skills or []
    course_skills = request.course_skills or []
    assessment_scores = request.assessment_scores or {}
    certifications = []

    # If trainee_id provided or infer from current user
    trainee = None
    if request.trainee_id:
        trainee = db.query(Trainee).filter(Trainee.id == request.trainee_id).first()
    elif current_user.trainee_profile:
        trainee = current_user.trainee_profile

    if trainee:
        if not trainee_skills:
            trainee_skills = [s.skill_name for s in trainee.skills]
        if not course_skills:
            t_rec = db.query(TrainingRecord).filter(TrainingRecord.trainee_id == trainee.id).first()
            if t_rec and t_rec.course and t_rec.course.required_skills:
                course_skills = t_rec.course.required_skills
        if not assessment_scores:
            assessments = db.query(Assessment).filter(Assessment.trainee_id == trainee.id).all()
            assessment_scores = {a.assessment_name: a.score for a in assessments}
        cert_records = db.query(Certification).filter(Certification.trainee_id == trainee.id).all()
        certifications = [c.certificate_number for c in cert_records]

    target_role = request.target_role or "Full Stack Developer"

    # Call production AIService (communicates with external AI API)
    ai_result = ai_service.analyze_trainee_skill_gap(
        trainee_skills=trainee_skills,
        course_skills=course_skills,
        assessment_scores=assessment_scores,
        certifications=certifications,
        target_role=target_role
    )

    job_readiness = ai_result.get("job_readiness", 0.0)
    skill_gap_score = round(100.0 - job_readiness, 1)

    # Transform matched skills for backwards compatibility with UI
    matched_skills = [
        {"skill": s, "match_pct": int(job_readiness), "proficiency": "ADVANCED"}
        for s in ai_result.get("strengths", [])
    ]

    response_payload = SkillGapResponse(
        target_role=target_role,
        skill_gap_score=skill_gap_score,
        job_readiness=job_readiness,
        strengths=ai_result.get("strengths", []),
        skill_gaps=ai_result.get("skill_gaps", []),
        matched_skills=matched_skills,
        missing_skills=ai_result.get("skill_gaps", []),
        recommended_skills=ai_result.get("recommended_skills", []),
        confidence_score=0.85,
        summary=ai_result.get("summary", ""),
        available=ai_result.get("available", True),
        error=ai_result.get("error")
    )

    # If trainee exists, persist longitudinal record
    if trainee and ai_result.get("available", False):
        gap_record = SkillGapAnalysis(
            trainee_id=trainee.id,
            target_role=target_role,
            skill_gap_score=skill_gap_score,
            matched_skills_json=ai_result.get("strengths", []),
            missing_skills_json=ai_result.get("skill_gaps", []),
            recommended_skills_json=ai_result.get("recommended_skills", []),
            job_readiness=job_readiness,
            summary=ai_result.get("summary", ""),
            confidence_score=0.85
        )
        db.add(gap_record)
        db.commit()

        log_audit_event(
            db=db,
            action="AI_ANALYSIS_REQUESTED",
            entity_type="TRAINEE",
            entity_id=str(trainee.id),
            user_id=current_user.id,
            details={"target_role": target_role, "job_readiness": job_readiness}
        )

    return response_payload

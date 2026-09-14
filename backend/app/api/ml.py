"""
NEXTUP ML API — Placement Risk Prediction & Intervention Recommendation
========================================================================
SIH26135 | Team Lumora

All predictions are clearly labelled as DEMO/SYNTHETIC until
real verified outcome data is available.
"""
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Trainee, Assessment, TraineeSkill, Certification, TrainingRecord, Intervention
from app.auth.jwt_handler import get_current_user
from app.models.models import User
from app.ml.risk_service import risk_service
from app.ml.recommendation_service import generate_recommendation
from app.ml.retraining_service import get_verified_outcomes_for_retraining
from app.utils.audit import log_audit_event

router = APIRouter(prefix="/ml", tags=["ML Risk & Recommendations"])


# ─── Schemas ──────────────────────────────────────────────────────────────────

class RiskPredictionRequest(BaseModel):
    trainee_id: Optional[int] = None
    # Override individual features (optional — will be inferred from DB if trainee_id given)
    attendance_pct: Optional[float] = Field(None, ge=0, le=100)
    assessment_avg_score: Optional[float] = Field(None, ge=0, le=100)
    certification_status: Optional[int] = Field(None, ge=0, le=1)
    skill_gap_score: Optional[float] = Field(None, ge=0, le=100)
    has_apprenticeship: Optional[int] = Field(None, ge=0, le=1)
    training_duration_weeks: Optional[int] = None
    prior_experience_years: Optional[int] = None
    num_job_applications: Optional[int] = None
    verified_skill_count: Optional[int] = None
    course_domain: Optional[str] = None
    state: Optional[str] = None


class RiskPredictionResponse(BaseModel):
    available: bool
    status: str = "PLANNED"
    risk_score: Optional[float]
    risk_level: str
    prob_placed: Optional[float] = None
    contributing_factors: List[str]
    disclaimer: str
    features_used: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class InterventionRecommendationRequest(BaseModel):
    trainee_id: Optional[int] = None
    risk_level: str = "MEDIUM"
    risk_score: float = 50.0
    missing_skills: List[str] = Field(default_factory=list)
    target_job: Optional[str] = None


class RetrainStatusResponse(BaseModel):
    status: str
    verified_outcomes: int
    total_outcomes: int
    min_required: int
    retraining_ready: bool
    message: str
    disclaimer: Optional[str] = None
    feedback_loop: str


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/predict-risk", response_model=RiskPredictionResponse)
def predict_placement_risk(
    request: RiskPredictionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Predict placement risk for a trainee.
    If trainee_id is provided, features are inferred from their training records.
    Individual feature overrides are allowed.
    """
    if risk_service.get_model_info().get("status") == "PLANNED":
        return RiskPredictionResponse(**risk_service.predict({}))
    features: Dict[str, Any] = {}

    if request.trainee_id:
        trainee = db.query(Trainee).filter(Trainee.id == request.trainee_id).first()
        if not trainee:
            raise HTTPException(status_code=404, detail="Trainee not found")

        # Infer features from database
        assessments = db.query(Assessment).filter(Assessment.trainee_id == trainee.id).all()
        avg_score = (
            sum(a.score for a in assessments) / len(assessments) if assessments else 65.0
        )
        tr = db.query(TrainingRecord).filter(TrainingRecord.trainee_id == trainee.id).first()
        attendance = tr.attendance_pct if tr else 75.0
        training_weeks = 12
        if tr and tr.start_date and tr.end_date:
            try:
                from datetime import datetime
                s = datetime.strptime(tr.start_date[:10], "%Y-%m-%d")
                e = datetime.strptime(tr.end_date[:10], "%Y-%m-%d")
                training_weeks = max(1, (e - s).days // 7)
            except Exception:
                pass

        certs = db.query(Certification).filter(Certification.trainee_id == trainee.id).all()
        skills = db.query(TraineeSkill).filter(TraineeSkill.trainee_id == trainee.id).all()

        features = {
            "attendance_pct": attendance,
            "assessment_avg_score": avg_score,
            "certification_status": 1 if certs else 0,
            "skill_gap_score": 50.0,  # default; overridden if passed
            "has_apprenticeship": 0,
            "training_duration_weeks": training_weeks,
            "prior_experience_years": 0,
            "num_job_applications": 0,
            "verified_skill_count": len(skills),
            "course_domain": (tr.course.domain if tr and tr.course else "Information Technology"),
            "state": trainee.state or "Maharashtra",
        }

    # Apply any explicit overrides from request
    for field in [
        "attendance_pct", "assessment_avg_score", "certification_status",
        "skill_gap_score", "has_apprenticeship", "training_duration_weeks",
        "prior_experience_years", "num_job_applications", "verified_skill_count",
        "course_domain", "state"
    ]:
        val = getattr(request, field, None)
        if val is not None:
            features[field] = val

    # Use defaults if no features at all
    if not features:
        features = {
            "attendance_pct": 75.0,
            "assessment_avg_score": 60.0,
            "certification_status": 0,
            "skill_gap_score": 50.0,
            "has_apprenticeship": 0,
            "training_duration_weeks": 12,
            "prior_experience_years": 0,
            "num_job_applications": 0,
            "verified_skill_count": 3,
            "course_domain": "Information Technology",
            "state": "Maharashtra",
        }

    result = risk_service.predict(features)

    if request.trainee_id and result.get("available"):
        log_audit_event(
            db=db,
            action="ML_RISK_PREDICTION",
            entity_type="TRAINEE",
            entity_id=str(request.trainee_id),
            user_id=current_user.id,
            details={"risk_level": result.get("risk_level"), "risk_score": result.get("risk_score")},
        )

    return RiskPredictionResponse(**result)


@router.get("/model-info")
def get_model_info(current_user: User = Depends(get_current_user)):
    """
    Return the model evaluation metrics, feature importances, and disclaimer.
    """
    info = risk_service.get_model_info()
    return info


@router.post("/recommend-intervention")
def recommend_intervention(
    request: InterventionRecommendationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Generate a personalized intervention recommendation based on risk + skill gap.
    Optionally persists the intervention record to the database.
    """
    trainee = None
    state = None
    if request.trainee_id:
        trainee = db.query(Trainee).filter(Trainee.id == request.trainee_id).first()
        if trainee:
            state = trainee.state

    rec = generate_recommendation(
        risk_level=request.risk_level,
        risk_score=request.risk_score,
        missing_skills=request.missing_skills,
        job_title=request.target_job,
        trainee_state=state,
    )

    # Persist to database
    if trainee:
        intervention = Intervention(
            trainee_id=trainee.id,
            risk_level=request.risk_level,
            risk_score=request.risk_score,
            trigger_reason=rec["trigger_reason"],
            title=rec["title"],
            description=rec["description"],
            target_skills=rec["target_skills"],
            recommended_actions=rec["recommended_actions"],
            status="RECOMMENDED",
        )
        db.add(intervention)
        db.commit()
        db.refresh(intervention)
        rec["intervention_id"] = intervention.id

        log_audit_event(
            db=db,
            action="INTERVENTION_CREATED",
            entity_type="TRAINEE",
            entity_id=str(trainee.id),
            user_id=current_user.id,
            details={"risk_level": request.risk_level, "title": rec["title"]},
        )

    return rec


@router.get("/retrain-status", response_model=RetrainStatusResponse)
def retraining_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Check the verified outcome pool and retraining readiness.
    Admin only in production; available to all roles for demonstration.
    """
    result = get_verified_outcomes_for_retraining(db)
    return RetrainStatusResponse(
        status=result.get("status", "UNKNOWN"),
        verified_outcomes=result.get("verified_outcomes", 0),
        total_outcomes=result.get("total_outcomes", 0),
        min_required=result.get("min_required", 100),
        retraining_ready=result.get("retraining_ready", False),
        message=result.get("message", ""),
        disclaimer=result.get("disclaimer"),
        feedback_loop=result.get("feedback_loop", "UNKNOWN"),
    )

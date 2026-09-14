"""
NEXTUP Interventions API
========================
CRUD endpoints for trainee intervention records.
SIH26135 | Team Lumora
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models.models import Trainee, Intervention, User
from app.auth.jwt_handler import get_current_user
from app.utils.audit import log_audit_event

router = APIRouter(prefix="/interventions", tags=["Interventions"])


class InterventionCreate(BaseModel):
    trainee_id: int
    risk_level: str = "MEDIUM"
    risk_score: Optional[float] = None
    trigger_reason: Optional[str] = None
    title: str
    description: Optional[str] = None
    target_skills: Optional[List[str]] = Field(default_factory=list)
    recommended_actions: Optional[List[str]] = Field(default_factory=list)


class InterventionStatusUpdate(BaseModel):
    status: str  # RECOMMENDED, IN_PROGRESS, COMPLETED, DISMISSED


class InterventionResponse(BaseModel):
    id: int
    trainee_id: int
    risk_level: str
    risk_score: Optional[float]
    trigger_reason: Optional[str]
    title: str
    description: Optional[str]
    target_skills: Optional[List[str]]
    recommended_actions: Optional[List[str]]
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.get("/trainee/{trainee_id}", response_model=List[InterventionResponse])
def list_trainee_interventions(
    trainee_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    trainee = db.query(Trainee).filter(Trainee.id == trainee_id).first()
    if not trainee:
        raise HTTPException(status_code=404, detail="Trainee not found")
    interventions = (
        db.query(Intervention)
        .filter(Intervention.trainee_id == trainee_id)
        .order_by(Intervention.created_at.desc())
        .all()
    )
    return interventions


@router.post("", response_model=InterventionResponse, status_code=status.HTTP_201_CREATED)
def create_intervention(
    payload: InterventionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    trainee = db.query(Trainee).filter(Trainee.id == payload.trainee_id).first()
    if not trainee:
        raise HTTPException(status_code=404, detail="Trainee not found")

    intervention = Intervention(
        trainee_id=payload.trainee_id,
        risk_level=payload.risk_level,
        risk_score=payload.risk_score,
        trigger_reason=payload.trigger_reason,
        title=payload.title,
        description=payload.description,
        target_skills=payload.target_skills or [],
        recommended_actions=payload.recommended_actions or [],
        status="RECOMMENDED",
    )
    db.add(intervention)
    db.commit()
    db.refresh(intervention)

    log_audit_event(
        db=db,
        action="INTERVENTION_CREATED",
        entity_type="TRAINEE",
        entity_id=str(payload.trainee_id),
        user_id=current_user.id,
        details={"title": payload.title, "risk_level": payload.risk_level},
    )
    return intervention


@router.patch("/{intervention_id}/status", response_model=InterventionResponse)
def update_intervention_status(
    intervention_id: int,
    payload: InterventionStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    VALID_STATUSES = {"RECOMMENDED", "IN_PROGRESS", "COMPLETED", "DISMISSED"}
    if payload.status not in VALID_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {VALID_STATUSES}",
        )
    intervention = db.query(Intervention).filter(Intervention.id == intervention_id).first()
    if not intervention:
        raise HTTPException(status_code=404, detail="Intervention not found")

    intervention.status = payload.status
    intervention.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(intervention)

    log_audit_event(
        db=db,
        action="INTERVENTION_STATUS_UPDATED",
        entity_type="INTERVENTION",
        entity_id=str(intervention_id),
        user_id=current_user.id,
        details={"new_status": payload.status},
    )
    return intervention

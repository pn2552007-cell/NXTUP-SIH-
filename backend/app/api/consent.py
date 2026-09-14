from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.database import get_db
from app.models.models import User, Trainee, Consent
from app.schemas.schemas import ConsentCreate, ConsentRevoke, ConsentResponse
from app.auth.jwt_handler import get_current_user
from app.utils.id_generator import generate_skillpulse_id
from app.utils.audit import log_audit_event

router = APIRouter(prefix="/consent", tags=["Consent Management"])

@router.get("/status")
def get_consent_status(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    trainee = db.query(Trainee).filter(Trainee.user_id == current_user.id).first()
    if not trainee:
        return {
            "has_trainee_profile": False,
            "consent_given": False,
            "skillpulse_id": None
        }

    latest_consent = db.query(Consent).filter(Consent.trainee_id == trainee.id).order_by(Consent.consented_at.desc()).first()
    nid = trainee.nextup_id or trainee.skillpulse_id
    return {
        "has_trainee_profile": True,
        "consent_given": trainee.consent_given,
        "nextup_id": nid,
        "skillpulse_id": trainee.skillpulse_id,
        "consent_version": latest_consent.consent_version if latest_consent else "v1.0",
        "purpose": latest_consent.purpose if latest_consent else "Longitudinal tracking of employment, retention, and wage growth outcomes",
        "revocation_status": latest_consent.revocation_status if latest_consent else False,
        "revocation_timestamp": latest_consent.revocation_timestamp if latest_consent else None,
        "consented_at": latest_consent.consented_at if latest_consent else None
    }

@router.post("", response_model=ConsentResponse)
def submit_consent(
    consent_in: ConsentCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    trainee = db.query(Trainee).filter(Trainee.user_id == current_user.id).first()
    if not trainee and current_user.role == "TRAINEE":
        unified_id = generate_skillpulse_id(db)
        trainee = Trainee(
            user_id=current_user.id,
            nextup_id=unified_id,
            skillpulse_id=unified_id,
            full_name=current_user.full_name,
            email=current_user.email,
            phone=current_user.phone,
            consent_given=consent_in.consent_status
        )
        db.add(trainee)
        db.flush()

    if trainee:
        # Backfill unified IDs created before nextup_id existed.
        if not trainee.nextup_id and trainee.skillpulse_id:
            trainee.nextup_id = trainee.skillpulse_id
        if not trainee.skillpulse_id and trainee.nextup_id:
            trainee.skillpulse_id = trainee.nextup_id
        trainee.consent_given = consent_in.consent_status
        db.flush()

    client_ip = request.client.host if request.client else "127.0.0.1"
    consent_record = Consent(
        user_id=current_user.id,
        trainee_id=trainee.id if trainee else None,
        consent_status=consent_in.consent_status,
        consent_version=consent_in.consent_version,
        purpose=consent_in.purpose,
        consent_text=consent_in.consent_text or "I consent to NEXTUP tracking my training and employment outcomes.",
        ip_address=client_ip,
        revocation_status=False,
        revocation_timestamp=None,
        consented_at=datetime.utcnow()
    )
    db.add(consent_record)
    db.commit()
    db.refresh(consent_record)

    log_audit_event(
        db=db,
        action="CONSENT_GRANTED" if consent_in.consent_status else "CONSENT_DENIED",
        entity_type="CONSENT",
        entity_id=str(consent_record.id),
        user_id=current_user.id,
        details={
            "version": consent_record.consent_version,
            "purpose": consent_record.purpose,
            "ip_address": client_ip,
            "trainee_id": trainee.id if trainee else None
        }
    )

    msg = "Consent granted and active for longitudinal tracking." if consent_in.consent_status else "Consent declined. Longitudinal tracking disabled."

    return ConsentResponse(
        id=consent_record.id,
        user_id=current_user.id,
        trainee_id=trainee.id if trainee else None,
        nextup_id=(trainee.nextup_id if trainee else None),
        skillpulse_id=trainee.skillpulse_id if trainee else None,
        consent_status=consent_record.consent_status,
        consent_version=consent_record.consent_version,
        purpose=consent_record.purpose,
        revocation_status=consent_record.revocation_status,
        consented_at=consent_record.consented_at,
        message=msg
    )

@router.post("/revoke")
def revoke_consent(
    revoke_in: ConsentRevoke,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    trainee = db.query(Trainee).filter(Trainee.user_id == current_user.id).first()
    if not trainee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trainee profile not found.")

    trainee.consent_given = False
    
    # Update latest consent record
    latest = db.query(Consent).filter(Consent.trainee_id == trainee.id).order_by(Consent.consented_at.desc()).first()
    now = datetime.utcnow()
    if latest:
        latest.revocation_status = True
        latest.revocation_timestamp = now
        latest.consent_status = False

    db.commit()

    log_audit_event(
        db=db,
        action="CONSENT_REVOKED",
        entity_type="CONSENT",
        entity_id=str(latest.id) if latest else None,
        user_id=current_user.id,
        details={"reason": revoke_in.reason, "revoked_at": now.isoformat()}
    )

    return {
        "status": "revoked",
        "consent_given": False,
        "revoked_at": now.isoformat(),
        "message": "Longitudinal outcome tracking consent has been successfully revoked."
    }

@router.get("/audit-trail")
def get_consent_audit_trail(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    trainee = db.query(Trainee).filter(Trainee.user_id == current_user.id).first()
    if not trainee and current_user.role != "ADMIN":
        return []

    query = db.query(Consent)
    if current_user.role != "ADMIN":
        query = query.filter(Consent.trainee_id == trainee.id)

    records = query.order_by(Consent.consented_at.desc()).all()
    return [
        {
            "id": c.id,
            "version": c.consent_version,
            "purpose": c.purpose,
            "status": "ACTIVE" if (c.consent_status and not c.revocation_status) else "REVOKED" if c.revocation_status else "DENIED",
            "consented_at": c.consented_at,
            "revocation_timestamp": c.revocation_timestamp,
            "ip_address": c.ip_address
        }
        for c in records
    ]

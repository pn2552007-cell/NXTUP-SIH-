"""Shared ownership and consent checks for longitudinal outcome operations."""
from fastapi import HTTPException
from app.models.models import Provider, TrainingRecord


def require_trainee_access(db, user, trainee, *, consent=True, providers=True):
    if trainee is None:
        raise HTTPException(404, "Trainee not found.")
    allowed = user.role == "ADMIN" or trainee.user_id == user.id
    if not allowed and providers and user.role in ("PROVIDER", "TRAINING_PROVIDER"):
        provider = db.query(Provider).filter(Provider.user_id == user.id).first()
        allowed = provider is not None and db.query(TrainingRecord).filter(
            TrainingRecord.provider_id == provider.id,
            TrainingRecord.trainee_id == trainee.id,
        ).first() is not None
    if not allowed:
        raise HTTPException(403, "This trainee is outside your account scope.")
    if consent and not trainee.consent_given:
        raise HTTPException(403, "Active trainee consent is required for outcome tracking.")


def employer_matches(employer, record):
    # Once linked, a company-name match must never override the employer ID.
    if not employer:
        return False
    if record.employer_id is not None:
        return record.employer_id == employer.id
    return (record.employer_name or "").strip().casefold() == employer.company_name.strip().casefold()
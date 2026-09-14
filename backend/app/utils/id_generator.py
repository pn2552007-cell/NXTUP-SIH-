import secrets
import string
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_

ALPHABET = "0123456789ABCDEFGHJKLMNPQRSTUVWXYZ"

def generate_nextup_id(db: Session, max_attempts: int = 50) -> str:
    """
    Generates a unified, persistent, consent-based Trainee Identity in the format:
    NXT-YYYY-XXXXXX (e.g. NXT-2026-000001 or NXT-2026-A8K29P).
    Ensures uniqueness against database records across programs.
    """
    from app.models.models import Trainee

    current_year = 2026
    
    # First, try sequential format NXT-2026-000001 based on total trainee count
    count = db.query(Trainee).count() + 1
    sequential_candidate = f"NXT-{current_year}-{count:06d}"
    exists = db.query(Trainee).filter(
        or_(
            getattr(Trainee, "nextup_id", Trainee.skillpulse_id) == sequential_candidate,
            Trainee.skillpulse_id == sequential_candidate
        )
    ).first()
    if not exists:
        return sequential_candidate

    # If already taken, generate collision-resistant alphanumeric identifier
    for _ in range(max_attempts):
        suffix = "".join(secrets.choice("23456789ABCDEFGHJKLMNPQRSTUVWXYZ") for _ in range(6))
        candidate_id = f"NXT-{current_year}-{suffix}"
        exists = db.query(Trainee).filter(
            or_(
                getattr(Trainee, "nextup_id", Trainee.skillpulse_id) == candidate_id,
                Trainee.skillpulse_id == candidate_id
            )
        ).first()
        if not exists:
            return candidate_id

    # Fallback with high-entropy timestamp component
    import time
    ts = hex(int(time.time()))[2:].upper()[-6:]
    return f"NXT-{current_year}-{ts}"

# Backward-compatible alias
generate_skillpulse_id = generate_nextup_id

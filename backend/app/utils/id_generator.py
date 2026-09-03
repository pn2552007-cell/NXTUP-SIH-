import secrets
import string
from sqlalchemy.orm import Session

ALPHABET = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"  # Excludes easily confused chars like 0, 1, O, I

def generate_skillpulse_id(db: Session, max_attempts: int = 20) -> str:
    """
    Generates a unique, non-sequential, persistent public SkillPulse ID in format SP-XXXXXXXX.
    Ensures uniqueness against database records.
    """
    from app.models.models import Trainee

    for _ in range(max_attempts):
        suffix = "".join(secrets.choice(ALPHABET) for _ in range(8))
        candidate_id = f"SP-{suffix}"
        exists = db.query(Trainee).filter(Trainee.skillpulse_id == candidate_id).first()
        if not exists:
            return candidate_id

    # Fallback with timestamp component if collision
    import time
    ts = hex(int(time.time()))[2:].upper()[-4:]
    random_part = "".join(secrets.choice(ALPHABET) for _ in range(4))
    return f"SP-{ts}{random_part}"

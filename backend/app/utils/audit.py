from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.models import AuditLog

def log_audit_event(
    db: Session,
    action: str,
    entity_type: str,
    entity_id: Optional[str] = None,
    user_id: Optional[int] = None,
    details: Optional[Dict[str, Any]] = None
) -> AuditLog:
    """
    Persists an immutable audit log entry for security and compliance.
    """
    entry = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id) if entity_id is not None else None,
        details_json=details or {},
        created_at=datetime.utcnow()
    )
    db.add(entry)
    db.commit()
    return entry

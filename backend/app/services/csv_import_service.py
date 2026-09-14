import csv
import io
import re
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.models.models import (
    User, Trainee, Provider, Course, TrainingRecord, Assessment,
    Certification, Skill, TraineeSkill, EmploymentRecord, Followup, Consent
)
from app.auth.jwt_handler import get_password_hash
from app.utils.id_generator import generate_skillpulse_id
from app.utils.skill_normalizer import normalize_skill_name, get_or_create_skill
from app.utils.audit import log_audit_event

class CsvImportService:
    """Service to parse, validate, and bulk-ingest trainee records uploaded by training providers."""

    @classmethod
    def process_trainee_roster(cls, db: Session, content: bytes, provider_id: int) -> Dict[str, Any]:
        return cls.import_trainees_csv(file_content=content, provider_id=provider_id, db=db)

    @classmethod
    def import_trainees_csv(cls, file_content: bytes, provider_id: int, db: Session) -> Dict[str, Any]:
        try:
            text_stream = io.StringIO(file_content.decode("utf-8-sig"))
        except UnicodeDecodeError:
            try:
                text_stream = io.StringIO(file_content.decode("latin1"))
            except Exception as e:
                return {
                    "total_records": 0,
                    "imported_count": 0,
                    "failed_count": 0,
                    "errors": [{"row": 0, "error": f"Encoding error: {str(e)}"}],
                    "message": "Failed to decode CSV file."
                }

        reader = csv.DictReader(text_stream)
        if not reader.fieldnames:
            return {
                "total_records": 0,
                "imported_count": 0,
                "failed_count": 0,
                "errors": [{"row": 0, "error": "CSV file is empty or missing headers."}],
                "message": "CSV file is empty or has no header row."
            }

        provider = db.query(Provider).filter(Provider.id == provider_id).first()
        imported_count = 0
        errors = []
        rows = list(reader)
        total_records = len(rows)

        for idx, row in enumerate(rows, start=2):
            try:
                full_name = row.get("full_name") or row.get("name") or ""
                email = row.get("email") or ""
                if not full_name.strip() or not email.strip():
                    errors.append({"row": idx, "error": "Missing full_name or email."})
                    continue

                clean_email = email.strip().lower()
                existing_user = db.query(User).filter(User.email == clean_email).first()

                if existing_user:
                    user = existing_user
                    trainee = existing_user.trainee_profile
                    if not trainee:
                        sp_id = generate_skillpulse_id(db)
                        trainee = Trainee(
                            user_id=user.id,
                            skillpulse_id=sp_id,
                            full_name=full_name.strip(),
                            email=clean_email,
                            consent_given=False
                        )
                        db.add(trainee)
                        db.flush()
                else:
                    user = User(
                        email=clean_email,
                        hashed_password=get_password_hash("NextUp@Init2026"),
                        role="TRAINEE",
                        full_name=full_name.strip(),
                        phone=row.get("phone", "").strip() or None,
                        is_active=True
                    )
                    db.add(user)
                    db.flush()

                    sp_id = generate_skillpulse_id(db)
                    trainee = Trainee(
                        user_id=user.id,
                        skillpulse_id=sp_id,
                        full_name=full_name.strip(),
                        email=clean_email,
                        phone=row.get("phone", "").strip() or None,
                        gender=row.get("gender", "").strip() or None,
                        education=row.get("education", "").strip() or None,
                        district=row.get("district", "").strip() or None,
                        state=row.get("state", "").strip() or None,
                        consent_given=False
                    )
                    db.add(trainee)
                    db.flush()

                course_name = row.get("course_name") or row.get("course") or "Vocational Training Program"
                domain = row.get("domain", "General Technical").strip()

                course = db.query(Course).filter(
                    Course.course_name.ilike(course_name.strip()),
                    Course.provider_id == provider_id
                ).first()

                if not course:
                    course = Course(
                        provider_id=provider_id,
                        course_name=course_name.strip(),
                        domain=domain,
                        duration_weeks=12
                    )
                    db.add(course)
                    db.flush()

                # Check if training record exists
                t_record = db.query(TrainingRecord).filter(
                    TrainingRecord.trainee_id == trainee.id,
                    TrainingRecord.course_id == course.id
                ).first()

                if not t_record:
                    t_record = TrainingRecord(
                        trainee_id=trainee.id,
                        course_id=course.id,
                        provider_id=provider_id,
                        start_date=row.get("start_date") or datetime.utcnow().strftime("%Y-%m-%d"),
                        end_date=row.get("end_date"),
                        completion_status="COMPLETED" if row.get("end_date") else "IN_PROGRESS",
                        attendance_pct=95.0
                    )
                    db.add(t_record)
                    db.flush()

                # Parse skills
                skills_str = row.get("skills", "")
                if skills_str:
                    raw_skills = re.split(r"[,;|]", skills_str)
                    for raw_s in raw_skills:
                        norm_s = normalize_skill_name(raw_s)
                        if norm_s:
                            get_or_create_skill(db, norm_s)
                            existing_ts = db.query(TraineeSkill).filter(
                                TraineeSkill.trainee_id == trainee.id,
                                TraineeSkill.skill_name.ilike(norm_s)
                            ).first()
                            if not existing_ts:
                                db.add(TraineeSkill(
                                    trainee_id=trainee.id,
                                    skill_name=norm_s,
                                    proficiency_level="INTERMEDIATE",
                                    is_verified=True
                                ))

                imported_count += 1
            except Exception as e:
                errors.append({"row": idx, "error": str(e)})

        db.commit()

        log_audit_event(
            db=db,
            action="CSV_TRAINEES_IMPORTED",
            entity_type="PROVIDER",
            entity_id=str(provider_id),
            details={"imported": imported_count, "failed": len(errors)}
        )

        return {
            "total_records": total_records,
            "imported_count": imported_count,
            "failed_count": len(errors),
            "errors": errors,
            "message": f"Successfully imported {imported_count} out of {total_records} records."
        }

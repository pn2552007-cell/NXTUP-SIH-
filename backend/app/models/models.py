from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Boolean, Float, DateTime, ForeignKey, Text, JSON
)
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="TRAINEE")  # TRAINEE, TRAINING_PROVIDER, EMPLOYER, ADMIN
    full_name = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    trainee_profile = relationship("Trainee", back_populates="user", uselist=False)
    provider_profile = relationship("Provider", back_populates="user", uselist=False)
    employer_profile = relationship("Employer", back_populates="user", uselist=False)
    consents = relationship("Consent", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")


class Consent(Base):
    __tablename__ = "consents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    trainee_id = Column(Integer, ForeignKey("trainees.id"), nullable=True)
    consent_status = Column(Boolean, default=False, nullable=False)
    consent_version = Column(String(50), default="v1.0")
    purpose = Column(String(255), default="Longitudinal tracking of employment, retention, and wage growth outcomes")
    consent_text = Column(Text, nullable=False)
    ip_address = Column(String(100), nullable=True)
    revocation_status = Column(Boolean, default=False)
    revocation_timestamp = Column(DateTime, nullable=True)
    consented_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="consents")
    trainee = relationship("Trainee", back_populates="consents")


class Trainee(Base):
    __tablename__ = "trainees"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    nextup_id = Column(String(50), unique=True, index=True, nullable=True)  # Unified ID e.g. NXT-2026-000001
    skillpulse_id = Column(String(50), unique=True, index=True, nullable=False)  # Legacy compatibility
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    phone = Column(String(50), nullable=True)
    state = Column(String(100), nullable=True, index=True)
    district = Column(String(100), nullable=True, index=True)
    education = Column(String(100), nullable=True)
    gender = Column(String(20), nullable=True)
    date_of_birth = Column(String(50), nullable=True)
    consent_given = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="trainee_profile")
    consents = relationship("Consent", back_populates="trainee")
    enrollments = relationship("Enrollment", back_populates="trainee")
    training_records = relationship("TrainingRecord", back_populates="trainee")
    assessments = relationship("Assessment", back_populates="trainee")
    certifications = relationship("Certification", back_populates="trainee")
    skills = relationship("TraineeSkill", back_populates="trainee")
    employment_records = relationship("EmploymentRecord", back_populates="trainee")
    followups = relationship("Followup", back_populates="trainee")
    wage_history = relationship("WageHistory", back_populates="trainee")
    skill_gap_analyses = relationship("SkillGapAnalysis", back_populates="trainee")
    interventions = relationship("Intervention", back_populates="trainee")
    outcomes = relationship("Outcome", back_populates="trainee")

    @property
    def unified_id(self) -> str:
        return self.nextup_id or self.skillpulse_id


class Provider(Base):
    __tablename__ = "providers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    organization_name = Column(String(255), nullable=False)
    code = Column(String(50), unique=True, index=True, nullable=False)
    contact_person = Column(String(255), nullable=True)
    email = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)
    state = Column(String(100), nullable=True, index=True)
    district = Column(String(100), nullable=True)
    accreditation_no = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="provider_profile")
    courses = relationship("Course", back_populates="provider")
    batches = relationship("TrainingBatch", back_populates="provider")
    training_records = relationship("TrainingRecord", back_populates="provider")


class Employer(Base):
    __tablename__ = "employers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    company_name = Column(String(255), nullable=False, index=True)
    industry = Column(String(100), nullable=True)
    contact_person = Column(String(255), nullable=True)
    email = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)
    state = Column(String(100), nullable=True)
    district = Column(String(100), nullable=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="employer_profile")
    verifications = relationship("EmployerVerification", back_populates="employer")
    employment_records = relationship("EmploymentRecord", back_populates="employer")


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=False)
    course_name = Column(String(255), nullable=False)
    domain = Column(String(100), nullable=False)  # IT, Healthcare, Manufacturing, Electronics
    duration_weeks = Column(Integer, default=12)
    description = Column(Text, nullable=True)
    target_roles = Column(JSON, nullable=True)  # List of target roles ["Full Stack Developer", "Backend Engineer"]
    required_skills = Column(JSON, nullable=True)  # List of normalized skills ["Python", "React", "SQL"]
    created_at = Column(DateTime, default=datetime.utcnow)

    provider = relationship("Provider", back_populates="courses")
    batches = relationship("TrainingBatch", back_populates="course")
    enrollments = relationship("Enrollment", back_populates="course")
    training_records = relationship("TrainingRecord", back_populates="course")
    certifications = relationship("Certification", back_populates="course")


class TrainingBatch(Base):
    __tablename__ = "training_batches"

    id = Column(Integer, primary_key=True, index=True)
    batch_code = Column(String(50), unique=True, index=True, nullable=False)
    batch_name = Column(String(255), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=False)
    trainer_name = Column(String(255), nullable=True)
    start_date = Column(String(50), nullable=True)
    end_date = Column(String(50), nullable=True)
    max_capacity = Column(Integer, default=30)
    created_at = Column(DateTime, default=datetime.utcnow)

    course = relationship("Course", back_populates="batches")
    provider = relationship("Provider", back_populates="batches")
    enrollments = relationship("Enrollment", back_populates="batch")
    training_records = relationship("TrainingRecord", back_populates="batch")


class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    trainee_id = Column(Integer, ForeignKey("trainees.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    batch_id = Column(Integer, ForeignKey("training_batches.id"), nullable=True)
    enrolled_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default="ENROLLED")  # ENROLLED, IN_PROGRESS, COMPLETED, DROPPED
    attendance_pct = Column(Float, default=100.0)
    completion_date = Column(String(50), nullable=True)

    trainee = relationship("Trainee", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")
    batch = relationship("TrainingBatch", back_populates="enrollments")


class TrainingRecord(Base):
    __tablename__ = "training_records"

    id = Column(Integer, primary_key=True, index=True)
    trainee_id = Column(Integer, ForeignKey("trainees.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=False)
    batch_id = Column(Integer, ForeignKey("training_batches.id"), nullable=True)
    cohort_id = Column(String(50), nullable=True)
    start_date = Column(String(50), nullable=True)
    end_date = Column(String(50), nullable=True)
    completion_status = Column(String(50), default="IN_PROGRESS")  # COMPLETED, IN_PROGRESS, DROPPED
    attendance_pct = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    trainee = relationship("Trainee", back_populates="training_records")
    course = relationship("Course", back_populates="training_records")
    provider = relationship("Provider", back_populates="training_records")
    batch = relationship("TrainingBatch", back_populates="training_records")
    assessments = relationship("Assessment", back_populates="training_record")


class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True)
    training_record_id = Column(Integer, ForeignKey("training_records.id"), nullable=True)
    trainee_id = Column(Integer, ForeignKey("trainees.id"), nullable=False)
    skill_name = Column(String(100), nullable=True)
    assessment_name = Column(String(255), nullable=False)
    assessment_type = Column(String(50), default="PRACTICAL")  # PRACTICAL, THEORY, PROJECT, FINAL
    score = Column(Float, nullable=False)
    max_score = Column(Float, default=100.0)
    pass_status = Column(Boolean, default=True)
    date_taken = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    training_record = relationship("TrainingRecord", back_populates="assessments")
    trainee = relationship("Trainee", back_populates="assessments")

    @property
    def percentage(self) -> float:
        if self.max_score and self.max_score > 0:
            return round((self.score / self.max_score) * 100.0, 2)
        return 0.0


class Certification(Base):
    __tablename__ = "certifications"

    id = Column(Integer, primary_key=True, index=True)
    trainee_id = Column(Integer, ForeignKey("trainees.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    certificate_number = Column(String(100), unique=True, index=True, nullable=False)
    issuing_organization = Column(String(255), nullable=True)
    issue_date = Column(String(50), nullable=True)
    expiry_date = Column(String(50), nullable=True)
    certificate_url = Column(String(500), nullable=True)
    related_skills = Column(JSON, nullable=True)
    status = Column(String(50), default="ISSUED")  # ISSUED, REVOKED, EXPIRED
    created_at = Column(DateTime, default=datetime.utcnow)

    trainee = relationship("Trainee", back_populates="certifications")
    course = relationship("Course", back_populates="certifications")


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)  # Normalized titlecase
    category = Column(String(100), nullable=True)  # Technical, Soft, Domain
    standard_code = Column(String(50), nullable=True)  # NSQF level code or standard
    created_at = Column(DateTime, default=datetime.utcnow)


class TraineeSkill(Base):
    __tablename__ = "trainee_skills"

    id = Column(Integer, primary_key=True, index=True)
    trainee_id = Column(Integer, ForeignKey("trainees.id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=True)
    skill_name = Column(String(100), nullable=False)
    proficiency_level = Column(String(50), default="INTERMEDIATE")  # BEGINNER, INTERMEDIATE, ADVANCED, EXPERT
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    trainee = relationship("Trainee", back_populates="skills")


class EmploymentRecord(Base):
    __tablename__ = "employment_records"

    id = Column(Integer, primary_key=True, index=True)
    trainee_id = Column(Integer, ForeignKey("trainees.id"), nullable=False)
    employer_id = Column(Integer, ForeignKey("employers.id"), nullable=True)
    employer_name = Column(String(255), nullable=True)
    job_title = Column(String(255), nullable=True)
    job_role = Column(String(255), nullable=True)
    industry = Column(String(100), nullable=True)
    employment_type = Column(String(50), default="FULL_TIME")  # FULL_TIME, CONTRACT, APPRENTICESHIP, INTERNSHIP
    location_city = Column(String(100), nullable=True)
    location_state = Column(String(100), nullable=True)
    joining_date = Column(String(50), nullable=True)
    starting_salary = Column(Float, nullable=True)
    current_salary = Column(Float, nullable=True)
    status = Column(String(50), default="SEEKING")  # SEEKING, EMPLOYED, SELF_EMPLOYED, NOT_SEEKING, UNKNOWN
    non_placement_reason = Column(String(255), nullable=True)
    verification_status = Column(String(50), default="PENDING")  # PENDING, VERIFIED, REJECTED
    verified_at = Column(DateTime, nullable=True)
    confidence_score = Column(Float, default=0.0)  # Calculated dynamically from verification logic
    created_at = Column(DateTime, default=datetime.utcnow)

    trainee = relationship("Trainee", back_populates="employment_records")
    employer = relationship("Employer", back_populates="employment_records")
    verifications = relationship("EmployerVerification", back_populates="employment_record")
    wage_histories = relationship("WageHistory", back_populates="employment_record")


Employment = EmploymentRecord


class EmployerVerification(Base):
    __tablename__ = "employer_verifications"

    id = Column(Integer, primary_key=True, index=True)
    employment_record_id = Column(Integer, ForeignKey("employment_records.id"), nullable=False)
    employer_id = Column(Integer, ForeignKey("employers.id"), nullable=False)
    verified_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(String(50), nullable=False)  # VERIFIED, REJECTED
    notes = Column(Text, nullable=True)
    verified_salary = Column(Float, nullable=True)
    verified_joining_date = Column(String(50), nullable=True)
    verified_job_title = Column(String(255), nullable=True)
    verification_source = Column(String(100), default="DIRECT_EMPLOYER_PORTAL")
    confidence_score = Column(Float, default=1.0)
    action_timestamp = Column(DateTime, default=datetime.utcnow)

    employment_record = relationship("EmploymentRecord", back_populates="verifications")
    employer = relationship("Employer", back_populates="verifications")


class Followup(Base):
    __tablename__ = "followups"

    id = Column(Integer, primary_key=True, index=True)
    trainee_id = Column(Integer, ForeignKey("trainees.id"), nullable=False)
    checkpoint = Column(String(50), nullable=False)  # 30_DAYS, 90_DAYS, 6_MONTHS, 12_MONTHS
    status = Column(String(50), default="SCHEDULED")  # SCHEDULED, SENT, RESPONDED, OVERDUE
    scheduled_date = Column(String(50), nullable=True)
    sent_at = Column(DateTime, nullable=True)
    responded_at = Column(DateTime, nullable=True)
    response_data = Column(JSON, nullable=True)  # {"employed": true, "same_employer": true, "salary": 24000, "satisfaction": 4}
    channel = Column(String(50), default="PORTAL")  # PORTAL, EMAIL, SMS, WHATSAPP
    sent_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    trainee = relationship("Trainee", back_populates="followups")


FollowUp = Followup


class WageHistory(Base):
    __tablename__ = "wage_history"

    id = Column(Integer, primary_key=True, index=True)
    trainee_id = Column(Integer, ForeignKey("trainees.id"), nullable=False)
    employment_record_id = Column(Integer, ForeignKey("employment_records.id"), nullable=True)
    salary_amount = Column(Float, nullable=False)
    currency = Column(String(10), default="INR")
    salary_period = Column(String(20), default="MONTHLY")  # MONTHLY, ANNUAL
    effective_date = Column(String(50), nullable=False)
    source = Column(String(50), default="TRAINEE_REPORTED")  # TRAINEE_REPORTED, EMPLOYER_VERIFIED, FOLLOWUP
    verification_status = Column(String(50), default="UNVERIFIED")  # UNVERIFIED, VERIFIED
    growth_pct_since_starting = Column(Float, default=0.0)
    notes = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    trainee = relationship("Trainee", back_populates="wage_history")
    employment_record = relationship("EmploymentRecord", back_populates="wage_histories")


class SkillGapAnalysis(Base):
    __tablename__ = "skill_gap_analysis"

    id = Column(Integer, primary_key=True, index=True)
    trainee_id = Column(Integer, ForeignKey("trainees.id"), nullable=False)
    target_role = Column(String(255), nullable=False)
    skill_gap_score = Column(Float, nullable=False)
    matched_skills_json = Column(JSON, nullable=False)  # list of matched skills / strengths
    missing_skills_json = Column(JSON, nullable=False)  # list of missing skills
    recommended_skills_json = Column(JSON, nullable=True)
    job_readiness = Column(Float, default=0.0)
    summary = Column(Text, nullable=True)
    confidence_score = Column(Float, default=0.85)
    created_at = Column(DateTime, default=datetime.utcnow)

    trainee = relationship("Trainee", back_populates="skill_gap_analyses")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(String(100), nullable=True)
    details_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="audit_logs")


# ─────────────────────────────────────────────────────────────────────────────
# NEXTUP New Entities: Job, JobRequirement, Intervention, Outcome
# ─────────────────────────────────────────────────────────────────────────────

class Job(Base):
    """Target industry job roles with salary ranges and demand levels."""
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    code = Column(String(50), unique=True, index=True, nullable=True)
    domain = Column(String(100), nullable=False)  # IT, Healthcare, Manufacturing, etc.
    description = Column(Text, nullable=True)
    salary_range_min = Column(Float, nullable=True)
    salary_range_max = Column(Float, nullable=True)
    demand_level = Column(String(20), default="MODERATE")  # LOW, MODERATE, HIGH, CRITICAL
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    requirements = relationship("JobRequirement", back_populates="job")


class JobRequirement(Base):
    """Skill requirements for target jobs — maps Job to Skill with importance weighting."""
    __tablename__ = "job_requirements"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=True)
    skill_name = Column(String(100), nullable=False)
    importance_weight = Column(Float, default=1.0)  # 0.0–1.0
    is_mandatory = Column(Boolean, default=True)
    min_proficiency = Column(String(50), default="INTERMEDIATE")  # BEGINNER, INTERMEDIATE, ADVANCED, EXPERT
    created_at = Column(DateTime, default=datetime.utcnow)

    job = relationship("Job", back_populates="requirements")
    skill = relationship("Skill")


class Intervention(Base):
    """Personalized intervention records generated from Risk + Skill Gap + Job Demand analysis."""
    __tablename__ = "interventions"

    id = Column(Integer, primary_key=True, index=True)
    trainee_id = Column(Integer, ForeignKey("trainees.id"), nullable=False)
    assigned_provider_id = Column(Integer, ForeignKey("providers.id"), nullable=True)
    risk_level = Column(String(20), nullable=False)  # LOW, MEDIUM, HIGH
    risk_score = Column(Float, nullable=True)
    trigger_reason = Column(String(255), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    target_skills = Column(JSON, nullable=True)  # list of skills to work on
    recommended_actions = Column(JSON, nullable=True)  # list of recommended actions
    status = Column(String(50), default="RECOMMENDED")  # RECOMMENDED, IN_PROGRESS, COMPLETED, DISMISSED
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    trainee = relationship("Trainee", back_populates="interventions")
    assigned_provider = relationship("Provider")


class Outcome(Base):
    """Verified longitudinal outcome records — closing the feedback loop for model retraining."""
    __tablename__ = "outcomes"

    id = Column(Integer, primary_key=True, index=True)
    trainee_id = Column(Integer, ForeignKey("trainees.id"), nullable=False)
    employment_record_id = Column(Integer, ForeignKey("employment_records.id"), nullable=True)
    placement_status = Column(Integer, nullable=False)  # 0 = not placed, 1 = placed
    retention_status_6m = Column(Integer, nullable=True)  # 0/1
    retention_status_12m = Column(Integer, nullable=True)  # 0/1
    starting_salary = Column(Float, nullable=True)
    current_salary = Column(Float, nullable=True)
    wage_growth_pct = Column(Float, nullable=True)
    is_verified = Column(Boolean, default=False)
    verification_source = Column(String(100), nullable=True)  # EMPLOYER_PORTAL, FOLLOWUP, ADMIN
    model_feedback_used = Column(Boolean, default=False)  # True once this outcome feeds model retraining
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    verified_at = Column(DateTime, nullable=True)

    trainee = relationship("Trainee", back_populates="outcomes")
    employment_record = relationship("EmploymentRecord")


# Alias for cleaner imports
TrainingProgram = Course

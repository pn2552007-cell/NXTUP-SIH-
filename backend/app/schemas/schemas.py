from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# ==================== AUTH & USER SCHEMAS ====================

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    full_name: str
    role: str = "TRAINEE"  # TRAINEE, TRAINING_PROVIDER, EMPLOYER, ADMIN
    phone: Optional[str] = None
    organization_name: Optional[str] = None  # for provider / employer
    state: Optional[str] = None
    district: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: int
    email: str
    full_name: str
    skillpulse_id: Optional[str] = None
    consent_given: bool = False

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    phone: Optional[str] = None
    is_active: bool
    created_at: datetime
    skillpulse_id: Optional[str] = None
    consent_given: bool = False

    class Config:
        from_attributes = True

# ==================== CONSENT SCHEMAS ====================

class ConsentCreate(BaseModel):
    consent_status: bool
    consent_version: str = "v1.0"
    purpose: str = "Longitudinal tracking of employment, retention, and wage growth outcomes"
    consent_text: Optional[str] = "I voluntarily agree to SkillPulse tracking my longitudinal skilling, certification, employment, retention, and wage progression."

class ConsentRevoke(BaseModel):
    reason: Optional[str] = "User requested consent revocation"

class ConsentResponse(BaseModel):
    id: int
    user_id: int
    trainee_id: Optional[int] = None
    skillpulse_id: Optional[str] = None
    consent_status: bool
    consent_version: str
    purpose: str
    revocation_status: bool
    consented_at: datetime
    message: str

# ==================== SKILL SCHEMAS ====================

class SkillCreate(BaseModel):
    name: str
    category: Optional[str] = "Technical"
    standard_code: Optional[str] = None

class SkillResponse(BaseModel):
    id: int
    name: str
    category: Optional[str] = None
    standard_code: Optional[str] = None

    class Config:
        from_attributes = True

class TraineeSkillCreate(BaseModel):
    skill_name: str
    proficiency_level: Optional[str] = "INTERMEDIATE"  # BEGINNER, INTERMEDIATE, ADVANCED, EXPERT

class TraineeSkillResponse(BaseModel):
    id: int
    skill_name: str
    proficiency_level: str
    is_verified: bool

    class Config:
        from_attributes = True

# ==================== COURSE & BATCH SCHEMAS ====================

class CourseCreate(BaseModel):
    course_name: str
    domain: str  # IT, Healthcare, Manufacturing, Electronics, etc.
    duration_weeks: int = 12
    description: Optional[str] = None
    target_roles: Optional[List[str]] = Field(default_factory=list)
    required_skills: Optional[List[str]] = Field(default_factory=list)

class CourseResponse(BaseModel):
    id: int
    provider_id: int
    course_name: str
    domain: str
    duration_weeks: int
    description: Optional[str] = None
    target_roles: Optional[List[str]] = None
    required_skills: Optional[List[str]] = None
    created_at: datetime

    class Config:
        from_attributes = True

class TrainingBatchCreate(BaseModel):
    course_id: int
    batch_name: str
    trainer_name: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    max_capacity: int = 30

class TrainingBatchResponse(BaseModel):
    id: int
    batch_code: str
    batch_name: str
    course_id: int
    provider_id: int
    trainer_name: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    max_capacity: int
    created_at: datetime

    class Config:
        from_attributes = True

class EnrollmentCreate(BaseModel):
    trainee_id: int
    course_id: int
    batch_id: Optional[int] = None

class EnrollmentResponse(BaseModel):
    id: int
    trainee_id: int
    course_id: int
    batch_id: Optional[int] = None
    status: str
    attendance_pct: float
    enrolled_at: datetime

    class Config:
        from_attributes = True

class CsvImportResponse(BaseModel):
    total_records: int
    imported_count: int
    failed_count: int
    errors: List[Dict[str, Any]] = Field(default_factory=list)
    message: str

# ==================== ASSESSMENT & CERTIFICATION SCHEMAS ====================

class AssessmentCreate(BaseModel):
    trainee_id: int
    assessment_name: str
    skill_name: Optional[str] = None
    assessment_type: Optional[str] = "PRACTICAL"
    score: float
    max_score: float = 100.0
    pass_status: bool = True
    date_taken: Optional[str] = None

class AssessmentResponse(BaseModel):
    id: int
    trainee_id: int
    assessment_name: str
    skill_name: Optional[str] = None
    score: float
    max_score: float
    percentage: float
    pass_status: bool
    date_taken: Optional[str] = None

    class Config:
        from_attributes = True

class CertificationCreate(BaseModel):
    trainee_id: int
    course_id: int
    issuing_organization: Optional[str] = None
    issue_date: Optional[str] = None
    expiry_date: Optional[str] = None
    certificate_url: Optional[str] = None
    related_skills: Optional[List[str]] = Field(default_factory=list)

class CertificationResponse(BaseModel):
    id: int
    trainee_id: int
    course_id: int
    certificate_number: str
    issuing_organization: Optional[str] = None
    issue_date: Optional[str] = None
    expiry_date: Optional[str] = None
    certificate_url: Optional[str] = None
    status: str

    class Config:
        from_attributes = True

# ==================== TRAINEE SCHEMAS ====================

class TraineeOnboard(BaseModel):
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    education: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[str] = None
    skills: Optional[List[str]] = Field(default_factory=list)

class TraineeResponse(BaseModel):
    id: int
    skillpulse_id: str
    full_name: str
    email: str
    phone: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    education: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[str] = None
    consent_given: bool
    created_at: datetime

    class Config:
        from_attributes = True

class TraineeProfileDetail(BaseModel):
    trainee: TraineeResponse
    skills: List[TraineeSkillResponse] = Field(default_factory=list)
    courses: List[Dict[str, Any]] = Field(default_factory=list)
    assessments: List[AssessmentResponse] = Field(default_factory=list)
    certifications: List[CertificationResponse] = Field(default_factory=list)
    employment_records: List[Dict[str, Any]] = Field(default_factory=list)
    followups: List[Dict[str, Any]] = Field(default_factory=list)
    wage_history: List[Dict[str, Any]] = Field(default_factory=list)

# ==================== AI SKILL GAP SCHEMAS ====================

class MatchedSkill(BaseModel):
    skill: str
    match_pct: int
    proficiency: Optional[str] = "INTERMEDIATE"

class SkillGapRequest(BaseModel):
    trainee_id: Optional[int] = None
    trainee_skills: Optional[List[str]] = None
    course_skills: Optional[List[str]] = None
    assessment_scores: Optional[Dict[str, float]] = None
    target_role: Optional[str] = "Full Stack Developer"

class SkillGapResponse(BaseModel):
    target_role: str
    skill_gap_score: float  # 0 to 100
    job_readiness: float    # 0 to 100
    strengths: List[str] = Field(default_factory=list)
    skill_gaps: List[str] = Field(default_factory=list)
    matched_skills: List[MatchedSkill] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    recommended_skills: List[str] = Field(default_factory=list)
    confidence_score: float = 0.85
    summary: str = ""
    available: bool = True
    error: Optional[str] = None

# ==================== EMPLOYMENT SCHEMAS ====================

class EmploymentReportRequest(BaseModel):
    status: str = "EMPLOYED"  # SEEKING, EMPLOYED, SELF_EMPLOYED, NOT_SEEKING
    employer_name: Optional[str] = None
    employer_id: Optional[int] = None
    job_title: Optional[str] = None
    job_role: Optional[str] = None
    industry: Optional[str] = None
    joining_date: Optional[str] = None
    starting_salary: Optional[float] = None
    current_salary: Optional[float] = None
    location_city: Optional[str] = None
    location_state: Optional[str] = None
    employment_type: Optional[str] = "FULL_TIME"

class EmploymentRecordResponse(BaseModel):
    id: int
    trainee_id: int
    employer_id: Optional[int] = None
    employer_name: Optional[str] = None
    job_title: Optional[str] = None
    job_role: Optional[str] = None
    industry: Optional[str] = None
    employment_type: str
    location_city: Optional[str] = None
    location_state: Optional[str] = None
    joining_date: Optional[str] = None
    starting_salary: Optional[float] = None
    current_salary: Optional[float] = None
    status: str
    verification_status: str
    confidence_score: float
    time_to_employment_days: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

# ==================== EMPLOYER VERIFICATION SCHEMAS ====================

class EmployerVerificationRequest(BaseModel):
    employment_record_id: int
    status: str  # VERIFIED, REJECTED
    notes: Optional[str] = None
    verified_salary: Optional[float] = None
    verified_joining_date: Optional[str] = None
    verified_job_title: Optional[str] = None

class EmployerVerificationResponse(BaseModel):
    id: int
    employment_record_id: int
    employer_id: int
    status: str
    confidence_score: float
    notes: Optional[str] = None
    action_timestamp: datetime

    class Config:
        from_attributes = True

# ==================== FOLLOW-UP SCHEMAS ====================

class FollowupRespondRequest(BaseModel):
    followup_id: int
    employed: bool
    job_title: Optional[str] = None
    employer_name: Optional[str] = None
    current_salary: Optional[float] = None
    satisfaction_score: Optional[int] = Field(default=None, ge=1, le=5)
    skills_used: Optional[List[str]] = Field(default_factory=list)

class FollowupResponse(BaseModel):
    id: int
    trainee_id: int
    checkpoint: str
    status: str
    scheduled_date: Optional[str] = None
    sent_at: Optional[datetime] = None
    responded_at: Optional[datetime] = None
    response_data: Optional[Dict[str, Any]] = None
    channel: str

    class Config:
        from_attributes = True

# ==================== WAGE HISTORY SCHEMAS ====================

class WageHistoryEntry(BaseModel):
    id: int
    effective_date: str
    salary_amount: float
    growth_pct_since_starting: float
    source: str
    verification_status: str
    notes: Optional[str] = None

    class Config:
        from_attributes = True

class WageGrowthResponse(BaseModel):
    trainee_id: int
    starting_salary: Optional[float] = None
    current_salary: Optional[float] = None
    overall_growth_pct: Optional[float] = None
    history: List[WageHistoryEntry] = Field(default_factory=list)
    has_history: bool = False
    message: Optional[str] = None

# ==================== ANALYTICS SCHEMAS (ZERO-DATA SAFE) ====================

class AnalyticsOverviewResponse(BaseModel):
    total_trainees: int = 0
    total_courses: int = 0
    total_providers: int = 0
    total_employers: int = 0
    total_certified: int = 0
    total_employed: int = 0
    employment_rate_pct: float = 0.0
    certification_rate_pct: float = 0.0
    retention_rate_6m_pct: Optional[float] = None
    retention_rate_12m_pct: Optional[float] = None
    retention_status: str = "Insufficient data"
    avg_wage_growth_pct: Optional[float] = None
    wage_growth_status: str = "No wage history available"
    median_time_to_employment_days: Optional[int] = None

class DistrictMetric(BaseModel):
    district: str
    state: str
    trainees: int = 0
    employed: int = 0
    employment_rate_pct: float = 0.0

class ProviderMetric(BaseModel):
    provider_id: int
    organization_name: str
    state: Optional[str] = None
    total_trained: int = 0
    certified: int = 0
    employed: int = 0
    employment_rate_pct: float = 0.0

class CourseMetric(BaseModel):
    course_id: int
    course_name: str
    domain: str
    total_enrolled: int = 0
    completed: int = 0
    employed: int = 0
    employment_rate_pct: float = 0.0

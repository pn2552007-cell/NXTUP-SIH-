"""
NXTUP Platform — Realistic Application Testing Dataset Generator
=================================================================
SIH 2026 | Problem ID: SIH26135 | Team Lumora

Generates a production-grade, diverse, and realistic testing dataset for:
1. Multi-stakeholder interaction testing (Admin, Training Providers, Employers, Trainees).
2. Longitudinal employment outcome and retention tracking (30d, 90d, 6m, 12m).
3. AI Skill-Gap analysis and automated remedial interventions.
4. Closed feedback loop verification (Outcome -> Retraining telemetry).
5. Safe, non-destructive execution: NEVER deletes or overwrites existing records.

Strictly follows project naming: 'NXTUP'.
"""

import os
import sys
import argparse
from datetime import datetime, timedelta

# Ensure backend root is on sys.path
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ROOT_DIR = os.path.abspath(os.path.join(BACKEND_DIR, ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

DEFAULT_DB_PATH = os.path.join(ROOT_DIR, "skillpulse.db").replace("\\", "/")

# Pre-flight argument parsing and connection check before importing models
parser = argparse.ArgumentParser(description="NXTUP Realistic Testing Dataset Generator")
parser.add_argument("--db", type=str, default=None, help="Custom Database connection URL")
cli_args, _ = parser.parse_known_args()

db_candidate = cli_args.db or os.environ.get("DATABASE_URL")
if not db_candidate:
    env_file = os.path.join(ROOT_DIR, ".env")
    if os.path.exists(env_file):
        try:
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip().startswith("DATABASE_URL="):
                        db_candidate = line.strip().split("=", 1)[1].strip().strip('"').strip("'")
                        break
        except Exception:
            pass

use_sqlite_fallback = False
if db_candidate and not db_candidate.startswith("sqlite"):
    try:
        from sqlalchemy import create_engine
        test_eng = create_engine(db_candidate, pool_pre_ping=True)
        with test_eng.connect() as conn:
            pass
    except Exception:
        print(f"[NXTUP Dataset] Configured database unreachable. Automatically using SQLite: sqlite:///{DEFAULT_DB_PATH}")
        db_candidate = f"sqlite:///{DEFAULT_DB_PATH}"
        use_sqlite_fallback = True

if db_candidate:
    os.environ["DATABASE_URL"] = db_candidate

if use_sqlite_fallback:
    import dotenv
    _orig_load_dotenv = dotenv.load_dotenv
    def _safe_load_dotenv(*args, **kwargs):
        kwargs["override"] = False
        res = _orig_load_dotenv(*args, **kwargs)
        os.environ["DATABASE_URL"] = f"sqlite:///{DEFAULT_DB_PATH}"
        return res
    dotenv.load_dotenv = _safe_load_dotenv


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.models.models import (
    Base, User, Trainee, Provider, Employer, Course, TrainingBatch,
    Enrollment, TrainingRecord, Assessment, Certification, Skill,
    TraineeSkill, EmploymentRecord, EmployerVerification, Followup,
    WageHistory, SkillGapAnalysis, Consent, Intervention, Outcome,
    Job, JobRequirement
)
from app.auth.jwt_handler import get_password_hash

DEMO_PWD = settings.DEMO_PASSWORD



def get_db_session(custom_db_url=None):
    """Establishes database connection with automatic fallback to local SQLite."""
    target_url = custom_db_url or settings.DATABASE_URL
    connect_args = {}
    if target_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}

    try:
        engine = create_engine(target_url, connect_args=connect_args, pool_pre_ping=True)
        with engine.connect() as conn:
            pass
        print(f"[NXTUP Dataset] Connected to primary database: {target_url.split('@')[-1] if '@' in target_url else target_url}")
    except Exception as err:
        fallback_url = f"sqlite:///{DEFAULT_DB_PATH}"
        print(f"[NXTUP Dataset] Primary database unreachable ({err}). Falling back to SQLite: {fallback_url}")
        engine = create_engine(fallback_url, connect_args={"check_same_thread": False})

    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return Session()


def seed_master_skills(db):
    """Populates master skills catalog if not present."""
    skills_catalog = [
        # IT & Web
        ("Python", "Technical", "NSQF-L6-IT01"),
        ("JavaScript", "Technical", "NSQF-L5-IT02"),
        ("React", "Technical", "NSQF-L6-IT03"),
        ("Node.js", "Technical", "NSQF-L6-IT04"),
        ("SQL", "Technical", "NSQF-L5-IT05"),
        ("REST APIs", "Technical", "NSQF-L5-IT06"),
        ("Git", "Technical", "NSQF-L4-IT07"),
        ("HTML/CSS", "Technical", "NSQF-L4-IT08"),
        ("TypeScript", "Technical", "NSQF-L6-IT09"),
        ("PostgreSQL", "Technical", "NSQF-L6-IT10"),
        ("Docker", "Technical", "NSQF-L6-IT11"),
        ("CI/CD", "Technical", "NSQF-L6-IT12"),
        # Cloud & DevOps
        ("Linux", "Technical", "NSQF-L5-CL01"),
        ("AWS", "Technical", "NSQF-L6-CL02"),
        ("Bash", "Technical", "NSQF-L4-CL03"),
        ("Kubernetes", "Technical", "NSQF-L7-CL04"),
        ("Terraform", "Technical", "NSQF-L7-CL05"),
        ("Networking", "Technical", "NSQF-L5-CL06"),
        # Data & AI
        ("Pandas", "Technical", "NSQF-L6-DA01"),
        ("NumPy", "Technical", "NSQF-L6-DA02"),
        ("Power BI", "Technical", "NSQF-L5-DA03"),
        ("Tableau", "Technical", "NSQF-L5-DA04"),
        ("Data Visualization", "Technical", "NSQF-L5-DA05"),
        ("Statistics", "Domain", "NSQF-L6-DA06"),
        ("Machine Learning", "Technical", "NSQF-L7-DA07"),
        ("Excel", "Technical", "NSQF-L4-DA08"),
        # Industrial IoT & Electronics
        ("C/C++", "Technical", "NSQF-L5-IOT01"),
        ("Embedded Systems", "Technical", "NSQF-L6-IOT02"),
        ("Microcontrollers", "Technical", "NSQF-L5-IOT03"),
        ("Sensors & Actuators", "Domain", "NSQF-L5-IOT04"),
        ("MQTT", "Technical", "NSQF-L6-IOT05"),
        ("PLC Programming", "Technical", "NSQF-L6-IOT06"),
        # Healthcare Operations
        ("Medical Terminology", "Domain", "NSQF-L4-HC01"),
        ("EHR Systems", "Domain", "NSQF-L5-HC02"),
        ("Healthcare Compliance & HIPAA", "Domain", "NSQF-L6-HC03"),
        ("Medical Coding (ICD-10)", "Domain", "NSQF-L6-HC04"),
    ]

    added = 0
    for name, cat, code in skills_catalog:
        if not db.query(Skill).filter(Skill.name == name).first():
            db.add(Skill(name=name, category=cat, standard_code=code))
            added += 1
    db.commit()
    print(f"[NXTUP Dataset] Master Skills catalog: {added} new skills seeded.")


def seed_admin_users(db, hashed_pwd):
    """Seeds distinct NXTUP Admin accounts."""
    admins = [
        ("audit.admin@nxtup.test", "Dr. V. K. Ramaswamy (National Quality Auditor)", "+91 98111 00101"),
        ("regional.admin@nxtup.test", "Smt. Shailaja Deshpande (Regional Mission Director)", "+91 98111 00102"),
    ]
    created = []
    for email, full_name, phone in admins:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(
                email=email,
                hashed_password=hashed_pwd,
                role="ADMIN",
                full_name=full_name,
                phone=phone,
                is_active=True
            )
            db.add(user)
            db.flush()
            print(f"[NXTUP Dataset] Created Admin: {email}")
        created.append(user)
    db.commit()
    return created


def seed_providers(db, hashed_pwd):
    """Seeds 4 realistic training providers across states."""
    provider_configs = [
        {
            "email": "nti.pune@nxtup.test",
            "org_name": "NXTUP National Technical Institute",
            "code": "PRV-NXT-NTI-001",
            "contact": "Prof. Anand Joshi",
            "phone": "+91 98200 11001",
            "state": "Maharashtra",
            "district": "Pune",
            "accreditation": "NSDC-NXT-2025-0101"
        },
        {
            "email": "cca.bangalore@nxtup.test",
            "org_name": "NXTUP Cyber & Cloud Academy",
            "code": "PRV-NXT-CCA-002",
            "contact": "Dr. Mythili Sundaram",
            "phone": "+91 98200 11002",
            "state": "Karnataka",
            "district": "Bengaluru Urban",
            "accreditation": "NSDC-NXT-2025-0102"
        },
        {
            "email": "iot.hyderabad@nxtup.test",
            "org_name": "NXTUP Precision IoT Skilling Centre",
            "code": "PRV-NXT-IOT-003",
            "contact": "Dr. K. S. Murthy",
            "phone": "+91 98200 11003",
            "state": "Telangana",
            "district": "Hyderabad",
            "accreditation": "NSDC-NXT-2025-0103"
        },
        {
            "email": "htc.chennai@nxtup.test",
            "org_name": "NXTUP HealthTech Training Collaborative",
            "code": "PRV-NXT-HTC-004",
            "contact": "Dr. Preeti Natarajan",
            "phone": "+91 98200 11004",
            "state": "Tamil Nadu",
            "district": "Chennai",
            "accreditation": "NSDC-NXT-2025-0104"
        }
    ]

    providers = []
    for cfg in provider_configs:
        user = db.query(User).filter(User.email == cfg["email"]).first()
        if not user:
            user = User(
                email=cfg["email"],
                hashed_password=hashed_pwd,
                role="TRAINING_PROVIDER",
                full_name=cfg["org_name"],
                phone=cfg["phone"],
                is_active=True
            )
            db.add(user)
            db.flush()

        prov = db.query(Provider).filter(Provider.code == cfg["code"]).first()
        if not prov:
            prov = Provider(
                user_id=user.id,
                organization_name=cfg["org_name"],
                code=cfg["code"],
                contact_person=cfg["contact"],
                email=cfg["email"],
                phone=cfg["phone"],
                state=cfg["state"],
                district=cfg["district"],
                accreditation_no=cfg["accreditation"]
            )
            db.add(prov)
            db.flush()
            print(f"[NXTUP Dataset] Created Provider: {cfg['org_name']} ({cfg['code']})")
        providers.append(prov)
    db.commit()
    return providers


def seed_employers(db, hashed_pwd):
    """Seeds 5 verified and realistic industry employers across sectors."""
    employer_configs = [
        {
            "email": "hr@nxtupcloud.test",
            "company_name": "NXTUP Cloud Systems Ltd",
            "industry": "Cloud Infrastructure & Enterprise IT",
            "contact": "Sandeep Nair (VP Talent Acquisition)",
            "phone": "+91 98300 22001",
            "state": "Karnataka",
            "district": "Bengaluru Urban",
            "is_verified": True
        },
        {
            "email": "careers@nxtuphealth.test",
            "company_name": "NXTUP HealthAnalytics Technologies",
            "industry": "Healthcare Informatics & EHR",
            "contact": "Ritu Sen (Head of People)",
            "phone": "+91 98300 22002",
            "state": "Telangana",
            "district": "Hyderabad",
            "is_verified": True
        },
        {
            "email": "talent@nxtupauto.test",
            "company_name": "NXTUP Precision Automation India",
            "industry": "Industrial IoT & Embedded Systems",
            "contact": "Vikram Sethi (Director HR)",
            "phone": "+91 98300 22003",
            "state": "Maharashtra",
            "district": "Pune",
            "is_verified": True
        },
        {
            "email": "recruitment@nxtupdigital.test",
            "company_name": "NXTUP Digital Enterprise Solutions",
            "industry": "Full-Stack Software Services",
            "contact": "Neha Agarwal (Sr. Recruiting Lead)",
            "phone": "+91 98300 22004",
            "state": "Haryana",
            "district": "Gurugram",
            "is_verified": True
        },
        {
            "email": "hiring@nxtupfintech.test",
            "company_name": "NXTUP NextGen Fintech Labs",
            "industry": "Fintech & Payment Platforms",
            "contact": "Farhan Siddiqui (Talent Partner)",
            "phone": "+91 98300 22005",
            "state": "Maharashtra",
            "district": "Mumbai",
            "is_verified": False  # Intentionally unverified for employer verification demo/test
        }
    ]

    employers = []
    for cfg in employer_configs:
        user = db.query(User).filter(User.email == cfg["email"]).first()
        if not user:
            user = User(
                email=cfg["email"],
                hashed_password=hashed_pwd,
                role="EMPLOYER",
                full_name=cfg["contact"],
                phone=cfg["phone"],
                is_active=True
            )
            db.add(user)
            db.flush()

        emp = db.query(Employer).filter(Employer.company_name == cfg["company_name"]).first()
        if not emp:
            emp = Employer(
                user_id=user.id,
                company_name=cfg["company_name"],
                industry=cfg["industry"],
                contact_person=cfg["contact"],
                email=cfg["email"],
                phone=cfg["phone"],
                state=cfg["state"],
                district=cfg["district"],
                is_verified=cfg["is_verified"]
            )
            db.add(emp)
            db.flush()
            print(f"[NXTUP Dataset] Created Employer: {cfg['company_name']}")
        employers.append(emp)
    db.commit()
    return employers


def seed_courses_and_batches(db, providers):
    """Seeds domain courses and batches."""
    course_configs = [
        {
            "provider": providers[0],  # NTI Pune
            "name": "NXTUP Full-Stack Web Architecture",
            "domain": "Information Technology",
            "duration": 16,
            "desc": "End-to-end full stack development: React, Node.js, Python, PostgreSQL, REST APIs.",
            "target_roles": ["Full Stack Developer", "Backend Engineer", "Frontend Developer"],
            "required_skills": ["Python", "JavaScript", "React", "SQL", "REST APIs", "Git", "HTML/CSS"]
        },
        {
            "provider": providers[1],  # CCA Bangalore
            "name": "NXTUP Cloud & DevOps Architecture",
            "domain": "Cloud Infrastructure",
            "duration": 14,
            "desc": "Container orchestration, Docker, AWS infrastructure, CI/CD pipelines, Linux administration.",
            "target_roles": ["Cloud & DevOps Engineer", "Site Reliability Associate", "Cloud Support Engineer"],
            "required_skills": ["Linux", "Docker", "AWS", "Git", "Bash", "Networking", "CI/CD"]
        },
        {
            "provider": providers[1],  # CCA Bangalore
            "name": "NXTUP Enterprise Data Analytics & AI",
            "domain": "Data Science & AI",
            "duration": 14,
            "desc": "Applied business intelligence, SQL data warehousing, Python data analysis, Power BI dashboards.",
            "target_roles": ["Data Analyst", "Business Intelligence Associate", "Junior Data Scientist"],
            "required_skills": ["Python", "SQL", "Excel", "Pandas", "Power BI", "Data Visualization", "Statistics"]
        },
        {
            "provider": providers[2],  # IOT Hyderabad
            "name": "NXTUP Industrial IoT Systems & Embedded Engineering",
            "domain": "Industrial Electronics",
            "duration": 16,
            "desc": "Microcontroller interfacing, embedded C/C++, MQTT protocol, PLC ladder logic, sensors telemetry.",
            "target_roles": ["Industrial IoT Specialist", "Embedded Systems Engineer", "Automation Associate"],
            "required_skills": ["C/C++", "Embedded Systems", "Microcontrollers", "Sensors & Actuators", "MQTT", "PLC Programming"]
        },
        {
            "provider": providers[3],  # HTC Chennai
            "name": "NXTUP Healthcare Informatics & EHR Operations",
            "domain": "Healthcare Technology",
            "duration": 12,
            "desc": "Digital health records, EHR workflows, ICD-10 medical coding, HIPAA privacy compliance.",
            "target_roles": ["Healthcare Data Coordinator", "Medical Records Analyst", "Clinical Data Associate"],
            "required_skills": ["Medical Terminology", "EHR Systems", "Healthcare Compliance & HIPAA", "Excel", "Medical Coding (ICD-10)"]
        }
    ]

    courses = []
    for c_cfg in course_configs:
        c = db.query(Course).filter(Course.course_name == c_cfg["name"]).first()
        if not c:
            c = Course(
                provider_id=c_cfg["provider"].id,
                course_name=c_cfg["name"],
                domain=c_cfg["domain"],
                duration_weeks=c_cfg["duration"],
                description=c_cfg["desc"],
                target_roles=c_cfg["target_roles"],
                required_skills=c_cfg["required_skills"]
            )
            db.add(c)
            db.flush()
            print(f"[NXTUP Dataset] Created Course: {c.course_name}")
        courses.append(c)

    # Batches
    batch_configs = [
        ("NXT-BATCH-2025-Q3-FS01", "Full-Stack Cohort Alpha", courses[0], providers[0], "Er. Rajesh Kulkarni", "2025-07-01", "2025-10-25"),
        ("NXT-BATCH-2025-Q4-FS02", "Full-Stack Cohort Beta", courses[0], providers[0], "Er. Priya Mahajan", "2025-10-01", "2026-01-28"),
        ("NXT-BATCH-2025-Q3-CD01", "Cloud DevOps Batch 1", courses[1], providers[1], "Dr. S. Venkatesh", "2025-08-01", "2025-11-15"),
        ("NXT-BATCH-2025-Q4-CD02", "Cloud DevOps Batch 2", courses[1], providers[1], "Dr. S. Venkatesh", "2025-11-01", "2026-02-18"),
        ("NXT-BATCH-2025-Q3-DA01", "Data Analytics Batch 1", courses[2], providers[1], "Prof. Rekha Rao", "2025-07-15", "2025-10-30"),
        ("NXT-BATCH-2025-Q4-DA02", "Data Analytics Batch 2", courses[2], providers[1], "Prof. Rekha Rao", "2025-10-15", "2026-01-30"),
        ("NXT-BATCH-2025-Q3-IOT01", "Industrial IoT Batch 1", courses[3], providers[2], "Er. Suresh Reddy", "2025-08-10", "2025-12-05"),
        ("NXT-BATCH-2025-Q4-HC01", "Healthcare Tech Batch 1", courses[4], providers[3], "Dr. Ananya Natarajan", "2025-09-01", "2025-11-30"),
    ]

    batches = []
    for code, b_name, crs, prov, trainer, s_date, e_date in batch_configs:
        b = db.query(TrainingBatch).filter(TrainingBatch.batch_code == code).first()
        if not b:
            b = TrainingBatch(
                batch_code=code,
                batch_name=b_name,
                course_id=crs.id,
                provider_id=prov.id,
                trainer_name=trainer,
                start_date=s_date,
                end_date=e_date,
                max_capacity=30
            )
            db.add(b)
            db.flush()
            print(f"[NXTUP Dataset] Created Batch: {code}")
        batches.append(b)

    db.commit()
    return courses, batches


def seed_trainees_and_journeys(db, hashed_pwd, providers, employers, courses, batches):
    """
    Seeds 35 diverse trainees spanning 5 realistic personas with complete
    relational journeys: Consent, Enrollment, TrainingRecord, Assessments,
    Certifications, TraineeSkills, SkillGapAnalysis, EmploymentRecord,
    EmployerVerification, Followups, WageHistory, Interventions, Outcomes.
    """
    # 35 Trainee demographic profiles across India
    trainee_profiles = [
        # 1-12: High Achievers (Persona A) - Tech/Cloud/Data, placed, verified, high wage growth
        ("Siddharth Sengupta", "Male", "B.Tech Computer Science", "Kolkata", "West Bengal", "2002-05-12", 0, 0),
        ("Ananya Swaminathan", "Female", "B.Tech IT", "Chennai", "Tamil Nadu", "2001-11-04", 1, 2),
        ("Kavya Nambiar", "Female", "B.Tech Electronics", "Thiruvananthapuram", "Kerala", "2002-08-22", 3, 6),
        ("Rohan Bhattacharya", "Male", "B.Sc Data Science", "Bengaluru Urban", "Karnataka", "2001-09-18", 2, 4),
        ("Pooja Kulkarni", "Female", "B.E Computer Science", "Pune", "Maharashtra", "2002-03-15", 0, 1),
        ("Aditya Vardhan", "Male", "B.Tech Cloud Computing", "Hyderabad", "Telangana", "2001-07-29", 1, 3),
        ("Tanvi Deshmukh", "Female", "BCA / MCA", "Nagpur", "Maharashtra", "2002-01-10", 0, 0),
        ("Naveen Raghavan", "Male", "B.Tech Electrical", "Coimbatore", "Tamil Nadu", "2001-12-05", 3, 6),
        ("Shreya Saxena", "Female", "B.Sc Statistics", "Lucknow", "Uttar Pradesh", "2002-06-17", 2, 5),
        ("Vikramaditya Solanki", "Male", "B.Tech IT", "Jaipur", "Rajasthan", "2001-04-20", 1, 2),
        ("Deepika Sundaram", "Female", "B.Sc Nursing / Health Informatics", "Madurai", "Tamil Nadu", "2002-02-14", 4, 7),
        ("Arjun Nair", "Male", "B.Tech Mechanical / IoT", "Kochi", "Kerala", "2001-10-30", 3, 6),

        # 13-24: Steady Performers (Persona B) - Placed in standard roles, solid progression
        ("Meera Joshi", "Female", "B.Sc IT", "Ahmedabad", "Gujarat", "2002-04-18", 0, 1),
        ("Nikhil Tiwari", "Male", "Diploma Computer Engg", "Varanasi", "Uttar Pradesh", "2003-01-12", 0, 0),
        ("Swati Rao", "Female", "BCA", "Bengaluru Urban", "Karnataka", "2002-09-25", 2, 4),
        ("Manish Chouhan", "Male", "B.Tech Mech", "Indore", "Madhya Pradesh", "2001-08-08", 3, 6),
        ("Divya Menon", "Female", "B.Sc Computer Science", "Kozhikode", "Kerala", "2002-07-19", 1, 3),
        ("Gaurav Bansal", "Male", "B.Com / Analytics", "Gurugram", "Haryana", "2001-03-11", 2, 5),
        ("Pallavi Patil", "Female", "B.E Electronics", "Kolhapur", "Maharashtra", "2002-10-02", 3, 6),
        ("Rahul Sengupta", "Male", "B.Tech IT", "Bhubaneswar", "Odisha", "2001-11-28", 0, 1),
        ("Archana Prabhu", "Female", "BCA", "Mangaluru", "Karnataka", "2002-12-14", 1, 2),
        ("Abhishek Mishra", "Male", "Diploma Electrical", "Ranchi", "Jharkhand", "2003-05-09", 3, 6),
        ("Sunita Mahajan", "Female", "B.Sc Microbiology / EHR", "Nashik", "Maharashtra", "2002-06-22", 4, 7),
        ("Tushar Gaikwad", "Male", "B.Tech IT", "Aurangabad", "Maharashtra", "2001-02-17", 0, 0),

        # 25-29: At-Risk / Under Intervention (Persona C) - Active job seeking, skill gaps
        ("Kiran Kumar Nayak", "Male", "B.Sc Math", "Patna", "Bihar", "2002-08-14", 0, 1),
        ("Monika Sethi", "Female", "Diploma IT", "Dehradun", "Uttarakhand", "2003-03-05", 1, 3),
        ("Vivek Dubey", "Male", "BCA", "Prayagraj", "Uttar Pradesh", "2002-11-19", 2, 5),
        ("Jaspreet Kaur", "Female", "B.Tech Electronics", "Amritsar", "Punjab", "2001-12-21", 3, 6),
        ("Sanjay Rathore", "Male", "B.Sc Physics", "Jodhpur", "Rajasthan", "2002-04-03", 0, 1),

        # 30-33: Apprenticeship / Transitioning (Persona D) - Industrial & Cloud apprenticeships
        ("Dinesh Gowda", "Male", "Diploma Mechanical", "Mysuru", "Karnataka", "2003-07-15", 3, 6),
        ("Bhavna Chauhan", "Female", "Diploma Health Admin", "Meerut", "Uttar Pradesh", "2002-09-09", 4, 7),
        ("Prateek Jain", "Male", "B.Tech CS", "Surat", "Gujarat", "2001-06-30", 1, 2),
        ("Nandini Varma", "Female", "B.Sc Computer Science", "Vadodara", "Gujarat", "2002-10-18", 2, 4),

        # 34-35: Dropout / Non-Placement / Special Cases (Persona E)
        ("Omkar Sawant", "Male", "Diploma Computer Technology", "Panaji", "Goa", "2003-02-28", 0, 0),
        ("Ritu Aggarwal", "Female", "B.A / Computer Basics", "Delhi", "Delhi", "2002-05-05", 4, 7),
    ]

    seeded_trainees = []

    for i, (name, gender, edu, dist, st, dob, crs_idx, b_idx) in enumerate(trainee_profiles, start=1):
        clean_prefix = name.lower().replace(" ", ".").replace("/", "")
        email = f"{clean_prefix}.test@nxtup.test"
        nxtup_id = f"NXT-2026-T{i:05d}"

        # 1. User Account
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(
                email=email,
                hashed_password=hashed_pwd,
                role="TRAINEE",
                full_name=name,
                phone=f"+91 98700 {10000 + i:05d}",
                is_active=True
            )
            db.add(user)
            db.flush()

        # 2. Trainee Record
        trainee = db.query(Trainee).filter(Trainee.nextup_id == nxtup_id).first()
        if not trainee:
            trainee = Trainee(
                user_id=user.id,
                nextup_id=nxtup_id,
                skillpulse_id=nxtup_id,  # Backward compatibility field
                full_name=name,
                email=email,
                phone=user.phone,
                state=st,
                district=dist,
                education=edu,
                gender=gender,
                date_of_birth=dob,
                consent_given=True
            )
            db.add(trainee)
            db.flush()

        # 3. DPDP Consent Record
        if not db.query(Consent).filter(Consent.trainee_id == trainee.id).first():
            db.add(Consent(
                user_id=user.id,
                trainee_id=trainee.id,
                consent_status=True,
                consent_version="v1.0",
                purpose="Longitudinal tracking of employment, retention, and wage growth outcomes",
                consent_text="I voluntarily consent to NXTUP tracking my training outcomes and verified career milestones for longitudinal workforce reporting.",
                ip_address=f"10.20.{i // 10 + 1}.{i % 250 + 10}"
            ))

        course = courses[crs_idx]
        batch = batches[b_idx]
        provider = batch.provider

        # Determine Persona Characteristics
        if i <= 12:
            persona = "HIGH_ACHIEVER"
            attendance = round(92.0 + (i % 6) * 1.2, 1)
            score = round(86.0 + (i % 11) * 1.1, 1)
            status_compl = "COMPLETED"
            certified = True
            is_employed = True
            start_salary = 28000.0 + (i % 5) * 2500.0
            curr_salary = start_salary * (1.30 + (i % 4) * 0.05)
            emp_status = "EMPLOYED"
            verification_status = "VERIFIED"
            conf_score = 0.96
            skill_gap = round(12.0 + (i % 5) * 2.5, 1)
            job_apps = 14 + (i % 6)
        elif i <= 24:
            persona = "STEADY"
            attendance = round(78.0 + (i % 8) * 1.3, 1)
            score = round(68.0 + (i % 12) * 1.2, 1)
            status_compl = "COMPLETED"
            certified = score >= 65.0
            is_employed = True
            start_salary = 20000.0 + (i % 4) * 1800.0
            curr_salary = start_salary * (1.18 + (i % 3) * 0.04)
            emp_status = "EMPLOYED"
            verification_status = "VERIFIED" if (i % 3 != 0) else "PENDING"
            conf_score = 0.88 if verification_status == "VERIFIED" else 0.65
            skill_gap = round(28.0 + (i % 6) * 2.8, 1)
            job_apps = 9 + (i % 7)
        elif i <= 29:
            persona = "AT_RISK"
            attendance = round(60.0 + (i % 7) * 1.8, 1)
            score = round(50.0 + (i % 10) * 1.2, 1)
            status_compl = "IN_PROGRESS"
            certified = False
            is_employed = False
            start_salary = None
            curr_salary = None
            emp_status = "SEEKING"
            verification_status = "PENDING"
            conf_score = 0.50
            skill_gap = round(52.0 + (i % 5) * 3.5, 1)
            job_apps = 8 + (i % 8)
        elif i <= 33:
            persona = "APPRENTICE"
            attendance = round(84.0 + (i % 4) * 1.5, 1)
            score = round(74.0 + (i % 5) * 1.4, 1)
            status_compl = "COMPLETED"
            certified = True
            is_employed = True
            start_salary = 16000.0 + (i % 3) * 2000.0
            curr_salary = start_salary * 1.20
            emp_status = "EMPLOYED"
            verification_status = "VERIFIED"
            conf_score = 0.90
            skill_gap = round(24.0 + (i % 4) * 2.0, 1)
            job_apps = 6 + (i % 4)
        else:
            persona = "DROPOUT"
            attendance = 48.5 if i == 34 else 54.0
            score = 42.0 if i == 34 else 45.0
            status_compl = "DROPPED"
            certified = False
            is_employed = False
            start_salary = None
            curr_salary = None
            emp_status = "NOT_SEEKING"
            verification_status = "NOT_APPLICABLE"
            conf_score = 0.40
            skill_gap = 68.0
            job_apps = 1

        # 4. Enrollment Record
        if not db.query(Enrollment).filter(Enrollment.trainee_id == trainee.id).first():
            db.add(Enrollment(
                trainee_id=trainee.id,
                course_id=course.id,
                batch_id=batch.id,
                enrolled_at=datetime.utcnow() - timedelta(days=240),
                status=status_compl,
                attendance_pct=attendance,
                completion_date=batch.end_date if status_compl == "COMPLETED" else None
            ))

        # 5. Training Record
        tr_rec = db.query(TrainingRecord).filter(TrainingRecord.trainee_id == trainee.id).first()
        if not tr_rec:
            tr_rec = TrainingRecord(
                trainee_id=trainee.id,
                course_id=course.id,
                provider_id=provider.id,
                batch_id=batch.id,
                cohort_id=batch.batch_code,
                start_date=batch.start_date,
                end_date=batch.end_date,
                completion_status=status_compl,
                attendance_pct=attendance
            )
            db.add(tr_rec)
            db.flush()

        # 6. Assessments (Theory, Practical, Final Capstone)
        if not db.query(Assessment).filter(Assessment.trainee_id == trainee.id).first():
            db.add(Assessment(
                training_record_id=tr_rec.id,
                trainee_id=trainee.id,
                assessment_name=f"{course.course_name} — Mid-Term Practical",
                assessment_type="PRACTICAL",
                score=round(max(score - 4.0, 30.0), 1),
                max_score=100.0,
                pass_status=score >= 50.0,
                date_taken="2025-09-20"
            ))
            db.add(Assessment(
                training_record_id=tr_rec.id,
                trainee_id=trainee.id,
                assessment_name=f"{course.course_name} — Final Certification Exam",
                assessment_type="FINAL",
                score=score,
                max_score=100.0,
                pass_status=score >= 60.0,
                date_taken="2025-11-10"
            ))

        # 7. Certification
        if certified and not db.query(Certification).filter(Certification.trainee_id == trainee.id).first():
            db.add(Certification(
                trainee_id=trainee.id,
                course_id=course.id,
                certificate_number=f"NXT-CERT-2026-{i:05d}",
                issuing_organization="National Council for Vocational Education and Training (NCVET)",
                issue_date="2025-11-20",
                status="ISSUED",
                related_skills=course.required_skills
            ))

        # 8. Trainee Skills
        if not db.query(TraineeSkill).filter(TraineeSkill.trainee_id == trainee.id).first():
            prof_level = "ADVANCED" if score > 84 else ("INTERMEDIATE" if score >= 65 else "BEGINNER")
            for sk_name in (course.required_skills or ["Technical Problem Solving"]):
                db.add(TraineeSkill(
                    trainee_id=trainee.id,
                    skill_name=sk_name,
                    proficiency_level=prof_level,
                    is_verified=certified
                ))

        # 9. Skill Gap Analysis
        if not db.query(SkillGapAnalysis).filter(SkillGapAnalysis.trainee_id == trainee.id).first():
            target_role = course.target_roles[0] if course.target_roles else "Technical Specialist"
            matched = [{"skill": s, "match_pct": int(score * 0.95), "proficiency": "ADVANCED" if score > 84 else "INTERMEDIATE"} for s in (course.required_skills[:3])]
            missing = ["Advanced Cloud Architecture", "Microservices Scaling"] if score > 75 else ["Docker", "AWS", "CI/CD Pipelines", "System Testing"]
            db.add(SkillGapAnalysis(
                trainee_id=trainee.id,
                target_role=target_role,
                skill_gap_score=skill_gap,
                matched_skills_json=matched,
                missing_skills_json=missing,
                recommended_skills_json=[f"Master {m} through hands-on project implementations" for m in missing],
                job_readiness=round(max(100.0 - skill_gap, 25.0), 1),
                summary=f"Trainee has evaluated competency profile for {target_role} with readiness score {round(max(100.0 - skill_gap, 25.0), 1)}%.",
                confidence_score=0.91
            ))

        # 10. Employment Record & Employer Verification
        assigned_emp = employers[i % len(employers)]
        emp_rec = db.query(EmploymentRecord).filter(EmploymentRecord.trainee_id == trainee.id).first()
        if not emp_rec:
            emp_rec = EmploymentRecord(
                trainee_id=trainee.id,
                employer_id=assigned_emp.id if is_employed else None,
                employer_name=assigned_emp.company_name if is_employed else None,
                job_title=f"{course.target_roles[0]}" if is_employed else None,
                job_role=course.domain if is_employed else None,
                industry=assigned_emp.industry if is_employed else None,
                employment_type="FULL_TIME" if persona != "APPRENTICE" else "APPRENTICESHIP",
                location_city=dist,
                location_state=st,
                joining_date="2025-12-01" if is_employed else None,
                starting_salary=start_salary,
                current_salary=round(curr_salary, 0) if curr_salary else None,
                status=emp_status,
                non_placement_reason="Pursuing higher technical qualifications" if persona == "DROPOUT" and i == 35 else ("Personal relocation" if persona == "DROPOUT" else None),
                verification_status=verification_status,
                verified_at=datetime.utcnow() - timedelta(days=60) if verification_status == "VERIFIED" else None,
                confidence_score=conf_score
            )
            db.add(emp_rec)
            db.flush()

        # Employer verification
        if verification_status == "VERIFIED" and not db.query(EmployerVerification).filter(EmployerVerification.employment_record_id == emp_rec.id).first():
            db.add(EmployerVerification(
                employment_record_id=emp_rec.id,
                employer_id=assigned_emp.id,
                verified_by_user_id=assigned_emp.user_id,
                status="VERIFIED",
                notes=f"Quarterly automated payroll verification confirmed active employment at {assigned_emp.company_name}.",
                verified_salary=curr_salary,
                verified_joining_date="2025-12-01",
                verified_job_title=emp_rec.job_title,
                verification_source="NXTUP_DIRECT_EMPLOYER_PORTAL",
                confidence_score=conf_score
            ))

        # 11. Wage History
        if is_employed and not db.query(WageHistory).filter(WageHistory.trainee_id == trainee.id).first():
            # Initial Joining
            db.add(WageHistory(
                trainee_id=trainee.id,
                employment_record_id=emp_rec.id,
                salary_amount=start_salary,
                effective_date="2025-12-01",
                source="EMPLOYER_VERIFIED" if verification_status == "VERIFIED" else "TRAINEE_REPORTED",
                verification_status=verification_status,
                growth_pct_since_starting=0.0,
                notes="Initial Placement Joining"
            ))
            # 6-Month Longitudinal increment
            if curr_salary and curr_salary > start_salary:
                growth_pct = round(((curr_salary - start_salary) / start_salary) * 100.0, 1)
                db.add(WageHistory(
                    trainee_id=trainee.id,
                    employment_record_id=emp_rec.id,
                    salary_amount=round(curr_salary, 0),
                    effective_date="2026-06-01",
                    source="EMPLOYER_VERIFIED" if verification_status == "VERIFIED" else "TRAINEE_REPORTED",
                    verification_status=verification_status,
                    growth_pct_since_starting=growth_pct,
                    notes="6-Month Longitudinal Performance Increment"
                ))

        # 12. Longitudinal Follow-ups (30d, 90d, 6m, 12m)
        if not db.query(Followup).filter(Followup.trainee_id == trainee.id).first():
            checkpoints = [
                ("30_DAYS", "2026-01-01", "RESPONDED"),
                ("90_DAYS", "2026-03-01", "RESPONDED" if is_employed else "SENT"),
                ("6_MONTHS", "2026-06-01", "RESPONDED" if (is_employed and verification_status == "VERIFIED") else "SCHEDULED"),
                ("12_MONTHS", "2026-12-01", "SCHEDULED")
            ]
            for cp_name, cp_date, cp_st in checkpoints:
                res_data = None
                if cp_st == "RESPONDED":
                    res_data = {
                        "employed": is_employed,
                        "employer": assigned_emp.company_name if is_employed else None,
                        "salary": round(curr_salary, 0) if curr_salary else None,
                        "same_employer": True,
                        "career_satisfaction": 5 if persona == "HIGH_ACHIEVER" else 4
                    }
                db.add(Followup(
                    trainee_id=trainee.id,
                    checkpoint=cp_name,
                    status=cp_st,
                    scheduled_date=cp_date,
                    sent_at=datetime.utcnow() - timedelta(days=90) if cp_st != "SCHEDULED" else None,
                    responded_at=datetime.utcnow() - timedelta(days=88) if cp_st == "RESPONDED" else None,
                    response_data=res_data,
                    channel="PORTAL",
                    sent_message=f"[NXTUP Followup] Longitudinal Milestone {cp_name} for {trainee.full_name}"
                ))

        # 13. Remedial Interventions (for At-Risk and Persona C)
        if persona == "AT_RISK" and not db.query(Intervention).filter(Intervention.trainee_id == trainee.id).first():
            db.add(Intervention(
                trainee_id=trainee.id,
                assigned_provider_id=provider.id,
                risk_level="HIGH" if score < 54 else "MEDIUM",
                risk_score=skill_gap,
                trigger_reason=f"Identified skill gap ({skill_gap}%) in {course.domain} target competency profile.",
                title=f"NXTUP Targeted Remedial Sprint — {course.target_roles[0]}",
                description=f"Prescriptive intervention to accelerate job readiness: targeted hands-on labs in {', '.join(course.required_skills[:3])}.",
                target_skills=course.required_skills[:3],
                recommended_actions=[
                    "Complete 2 dedicated hands-on sprint assignments",
                    "Attend 1-on-1 industry mentor review session",
                    "Revise mock interview questions and portfolio documentation",
                    f"Submit at least 3 curated job applications per week in {dist}"
                ],
                status="IN_PROGRESS" if i % 2 == 0 else "RECOMMENDED"
            ))

        # 14. Longitudinal Outcome records (closing feedback loop for retraining)
        if not db.query(Outcome).filter(Outcome.trainee_id == trainee.id).first():
            db.add(Outcome(
                trainee_id=trainee.id,
                employment_record_id=emp_rec.id if emp_rec else None,
                placement_status=1 if is_employed else 0,
                retention_status_6m=1 if (is_employed and persona in ["HIGH_ACHIEVER", "STEADY", "APPRENTICE"]) else 0,
                retention_status_12m=1 if (is_employed and persona == "HIGH_ACHIEVER") else None,
                starting_salary=start_salary,
                current_salary=round(curr_salary, 0) if curr_salary else None,
                wage_growth_pct=round(((curr_salary - start_salary) / start_salary) * 100.0, 1) if (curr_salary and start_salary) else 0.0,
                is_verified=(verification_status == "VERIFIED"),
                verification_source="DIRECT_EMPLOYER_PORTAL" if verification_status == "VERIFIED" else None,
                model_feedback_used=False,
                notes=f"NXTUP longitudinal outcome tracking record for cohort {batch.batch_code}."
            ))

        seeded_trainees.append(trainee)

    db.commit()
    print(f"[NXTUP Dataset] Seeded {len(seeded_trainees)} diverse Trainees with longitudinal journeys.")
    return seeded_trainees


def print_database_summary(db):
    """Prints a clear summary of database entity counts."""
    print("\n" + "=" * 65)
    print("       NXTUP APPLICATION TESTING DATASET SUMMARY")
    print("=" * 65)
    counts = [
        ("Users", User),
        ("Trainees", Trainee),
        ("Training Providers", Provider),
        ("Industry Employers", Employer),
        ("Master Skills", Skill),
        ("Courses", Course),
        ("Training Batches", TrainingBatch),
        ("Enrollments", Enrollment),
        ("Training Records", TrainingRecord),
        ("Assessments", Assessment),
        ("Certifications", Certification),
        ("Trainee Skills", TraineeSkill),
        ("Skill Gap Analyses", SkillGapAnalysis),
        ("Employment Records", EmploymentRecord),
        ("Employer Verifications", EmployerVerification),
        ("Wage Histories", WageHistory),
        ("Longitudinal Followups", Followup),
        ("Remedial Interventions", Intervention),
        ("Longitudinal Outcomes", Outcome),
        ("Target Jobs", Job),
        ("Job Requirements", JobRequirement),
    ]
    for label, model in counts:
        cnt = db.query(model).count()
        print(f"  {label:<28}: {cnt:>5} records")
    print("=" * 65)


def main():
    parser = argparse.ArgumentParser(description="NXTUP Realistic Testing Dataset Generator")
    parser.add_argument("--db", type=str, default=None, help="Custom Database connection URL")
    args = parser.parse_args()

    print("\n[NXTUP] Starting Realistic Testing Dataset Generation...")
    db = get_db_session(args.db)

    hashed_pwd = get_password_hash(DEMO_PWD)

    # 1. Master Skills Catalog
    seed_master_skills(db)

    # 2. Admin Users
    admins = seed_admin_users(db, hashed_pwd)

    # 3. Training Providers
    providers = seed_providers(db, hashed_pwd)

    # 4. Industry Employers
    employers = seed_employers(db, hashed_pwd)

    # 5. Courses and Training Batches
    courses, batches = seed_courses_and_batches(db, providers)

    # 6. Trainees & Complete Longitudinal Journeys
    seed_trainees_and_journeys(db, hashed_pwd, providers, employers, courses, batches)

    # 7. Print Final Database Counts
    print_database_summary(db)
    db.close()
    print("[NXTUP] Dataset generation completed successfully!\n")


if __name__ == "__main__":
    main()

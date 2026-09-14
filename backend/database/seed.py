import os
import sys
from datetime import datetime, timedelta

# Reconfigure stdout/stderr for utf-8 on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import SessionLocal, engine, Base
from app.models.models import (
    User, Trainee, Provider, Employer, Course, TrainingRecord, Assessment,
    Certification, Skill, TraineeSkill, EmploymentRecord, EmployerVerification,
    Followup, WageHistory, SkillGapAnalysis, Consent, Intervention, Outcome, Job, JobRequirement
)
from app.auth.jwt_handler import get_password_hash
from app.config import settings

DEMO_PWD = settings.DEMO_PASSWORD

def seed_database():
    print("🚀 Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Clear existing demo data to ensure a clean state
    print("Cleaning existing NEXTUP demo data...")
    try:
        db.query(Intervention).delete()
        db.query(Outcome).delete()
        db.query(JobRequirement).delete()
        db.query(Job).delete()
    except Exception:
        db.rollback()
    db.query(EmployerVerification).delete()
    db.query(WageHistory).delete()
    db.query(Followup).delete()
    db.query(SkillGapAnalysis).delete()
    db.query(EmploymentRecord).delete()
    db.query(TraineeSkill).delete()
    db.query(Certification).delete()
    db.query(Assessment).delete()
    db.query(TrainingRecord).delete()
    db.query(Consent).delete()
    db.query(Trainee).delete()
    db.query(Course).delete()
    db.query(Employer).delete()
    db.query(Provider).delete()
    db.query(Skill).delete()
    db.query(User).delete()
    db.commit()

    hashed_pwd = get_password_hash(DEMO_PWD)

    print("Creating Core Demo Users (NEXTUP Demo — SIH26135 | Team Lumora)...")
    # 1. Admin User
    admin_user = User(
        email="admin@nextup.demo",
        hashed_password=hashed_pwd,
        role="ADMIN",
        full_name="Dr. Rajeshwari Sengupta (Joint Secretary)",
        phone="+91 98110 01100",
        is_active=True
    )
    db.add(admin_user)

    # 2. Primary Provider User
    provider_user = User(
        email="provider@nextup.demo",
        hashed_password=hashed_pwd,
        role="PROVIDER",
        full_name="National Skill Training Academy",
        phone="+91 98220 22000",
        is_active=True
    )
    db.add(provider_user)

    # 3. Primary Employer User
    employer_user = User(
        email="employer@nextup.demo",
        hashed_password=hashed_pwd,
        role="EMPLOYER",
        full_name="Vikramaditya Rao (HR Talent Director)",
        phone="+91 98330 33000",
        is_active=True
    )
    db.add(employer_user)

    # 4. Primary Trainee User
    trainee_user = User(
        email="trainee@nextup.demo",
        hashed_password=hashed_pwd,
        role="TRAINEE",
        full_name="Aarav Sharma",
        phone="+91 98765 43210",
        is_active=True
    )
    db.add(trainee_user)
    db.flush()

    # -------------------------------------------------------------
    # 3 Training Providers
    # -------------------------------------------------------------
    print("🏫 Creating 3 Training Providers...")
    provider_1 = Provider(
        user_id=provider_user.id,
        organization_name="National Skill Training Academy",
        code="PRV-NSTA-001",
        contact_person="Dr. Sunita Deshmukh",
        email="provider@nextup.demo",
        phone="+91 98220 22000",
        state="Maharashtra",
        district="Pune",
        accreditation_no="NSDC-ACC-2024-8891"
    )
    db.add(provider_1)

    provider_user_2 = User(
        email="techempower@nextup.demo",
        hashed_password=hashed_pwd,
        role="PROVIDER",
        full_name="TechEmpower Skilling Foundation",
        phone="+91 98220 22001",
        is_active=True
    )
    db.add(provider_user_2)
    db.flush()

    provider_2 = Provider(
        user_id=provider_user_2.id,
        organization_name="TechEmpower Skilling Foundation",
        code="PRV-TESF-002",
        contact_person="Ramesh Narayanan",
        email="contact@techempower.org",
        phone="+91 98220 22001",
        state="Karnataka",
        district="Bengaluru Urban",
        accreditation_no="NSDC-ACC-2024-4112"
    )
    db.add(provider_2)

    provider_user_3 = User(
        email="apexdigital@nextup.demo",
        hashed_password=hashed_pwd,
        role="PROVIDER",
        full_name="Apex Digital Institute",
        phone="+91 98220 22002",
        is_active=True
    )
    db.add(provider_user_3)
    db.flush()

    provider_3 = Provider(
        user_id=provider_user_3.id,
        organization_name="Apex Digital Institute",
        code="PRV-APEX-003",
        contact_person="Kavita Murthy",
        email="admissions@apexdigital.edu",
        phone="+91 98220 22002",
        state="Tamil Nadu",
        district="Chennai",
        accreditation_no="NSDC-ACC-2024-1092"
    )
    db.add(provider_3)
    db.flush()

    providers_list = [provider_1, provider_2, provider_3]

    # -------------------------------------------------------------
    # 5 Courses
    # -------------------------------------------------------------
    print("📚 Creating 5 High-Impact Skilling Courses...")
    course_1 = Course(
        provider_id=provider_1.id,
        course_name="Full-Stack Web Development",
        domain="Information Technology",
        duration_weeks=16,
        description="Comprehensive full-stack engineering curriculum covering React, Node.js, Python, PostgreSQL, and REST APIs.",
        target_roles=["Full Stack Developer", "Frontend Engineer", "Backend Developer"],
        required_skills=["JavaScript", "React", "Python", "SQL", "REST APIs", "Git", "HTML/CSS"]
    )
    course_2 = Course(
        provider_id=provider_1.id,
        course_name="Cloud & DevOps Engineering",
        domain="Cloud Infrastructure",
        duration_weeks=14,
        description="Infrastructure automation, Linux system administration, Docker containerization, AWS fundamentals, and CI/CD pipelines.",
        target_roles=["Cloud & DevOps Engineer", "Site Reliability Associate", "Cloud Support Engineer"],
        required_skills=["Linux", "Docker", "AWS", "Git", "Bash", "Networking", "CI/CD"]
    )
    course_3 = Course(
        provider_id=provider_2.id,
        course_name="Data Analytics & AI",
        domain="Data Science & AI",
        duration_weeks=14,
        description="Business analytics, SQL data querying, Python data analysis with Pandas/NumPy, interactive Power BI dashboards, and ML basics.",
        target_roles=["Data Analyst", "Business Intelligence Associate", "Junior Data Scientist"],
        required_skills=["Python", "SQL", "Excel", "Pandas", "Power BI", "Data Visualization", "Statistics"]
    )
    course_4 = Course(
        provider_id=provider_2.id,
        course_name="Industrial IoT & Automation",
        domain="Industrial Electronics",
        duration_weeks=16,
        description="Hardware interfacing, embedded C/C++, microcontrollers, MQTT telemetry, PLC ladder logic, and industrial sensors.",
        target_roles=["Industrial IoT & Automation Specialist", "Embedded Systems Engineer", "Automation Associate"],
        required_skills=["C/C++", "Embedded Systems", "Microcontrollers", "Sensors & Actuators", "MQTT", "PLC Programming"]
    )
    course_5 = Course(
        provider_id=provider_3.id,
        course_name="Healthcare Data Operations",
        domain="Healthcare Technology",
        duration_weeks=12,
        description="Healthcare records management, EHR workflows, ICD-10 medical coding, FHIR standards, HIPAA privacy compliance, and health data reporting.",
        target_roles=["Healthcare Data Operations", "Medical Records Analyst", "Clinical Data Coordinator"],
        required_skills=["Medical Terminology", "EHR Systems", "Healthcare Compliance & HIPAA", "Excel", "Medical Coding (ICD-10)"]
    )
    db.add_all([course_1, course_2, course_3, course_4, course_5])
    db.flush()
    courses_list = [course_1, course_2, course_3, course_4, course_5]

    # -------------------------------------------------------------
    # 10 Employers
    # -------------------------------------------------------------
    print("🏢 Creating 10 Verified Industry Employers...")
    employer_specs = [
        ("Tata Consultancy Services", "IT & Global Software Services", "Mumbai", "Maharashtra", employer_user.id),
        ("Infosys Technologies", "Enterprise Digital Transformation", "Bengaluru", "Karnataka", None),
        ("Wipro Digital", "Cloud & IT Infrastructure", "Bengaluru", "Karnataka", None),
        ("Zomato Tech", "E-Commerce & Supply Chain Logistics", "Gurugram", "Haryana", None),
        ("Swiggy Engineering", "Consumer Tech & Quick Commerce", "Bengaluru", "Karnataka", None),
        ("Reliance Digital / Jio Platforms", "Telecommunications & Cloud Services", "Navi Mumbai", "Maharashtra", None),
        ("LTI Mindtree", "Cloud Consulting & Enterprise Apps", "Pune", "Maharashtra", None),
        ("HCLTech", "Digital Engineering & IoT Systems", "Noida", "Uttar Pradesh", None),
        ("Paytm Labs", "Fintech & Digital Payments", "Noida", "Uttar Pradesh", None),
        ("Apollo HealthTech", "Digital Health & Clinical Operations", "Hyderabad", "Telangana", None)
    ]

    employers_list = []
    for comp_name, ind, city, st, u_id in employer_specs:
        emp = Employer(
            user_id=u_id,
            company_name=comp_name,
            industry=ind,
            contact_person="Talent Acquisition Team",
            email=f"careers@{comp_name.lower().replace(' ', '').replace('/', '')}.com",
            phone="+91 98440 44000",
            state=st,
            district=city,
            is_verified=True
        )
        db.add(emp)
        employers_list.append(emp)
    db.flush()

    # -------------------------------------------------------------
    # Primary Trainee Profile (Aarav Sharma)
    # -------------------------------------------------------------
    print("Creating Primary Demo Trainee (Aarav Sharma - NXT-2026-000001)...")
    primary_trainee = Trainee(
        user_id=trainee_user.id,
        nextup_id="NXT-2026-000001",
        skillpulse_id="NXT-2026-000001",
        full_name="Aarav Sharma",
        email="trainee@nextup.demo",
        phone="+91 98765 43210",
        state="Maharashtra",
        district="Pune",
        education="B.Tech Computer Science",
        gender="Male",
        date_of_birth="2002-04-14",
        consent_given=True
    )
    db.add(primary_trainee)
    db.flush()

    # Consent record
    primary_consent = Consent(
        user_id=trainee_user.id,
        trainee_id=primary_trainee.id,
        consent_status=True,
        consent_version="v1.0",
        consent_text="I voluntarily agree to NEXTUP tracking my training and employment outcomes for public good.",
        ip_address="192.168.1.10"
    )
    db.add(primary_consent)

    # Training record
    primary_tr = TrainingRecord(
        trainee_id=primary_trainee.id,
        course_id=course_1.id,
        provider_id=provider_1.id,
        cohort_id="COHORT-2025-Q3",
        start_date="2025-08-01",
        end_date="2025-11-20",
        completion_status="COMPLETED",
        attendance_pct=96.5
    )
    db.add(primary_tr)
    db.flush()

    # Assessment
    primary_ass = Assessment(
        training_record_id=primary_tr.id,
        trainee_id=primary_trainee.id,
        assessment_name="Full Stack Software Engineering Certification Exam",
        score=91.5,
        max_score=100.0,
        pass_status=True,
        date_taken="2025-11-22"
    )
    db.add(primary_ass)

    # Certification
    primary_cert = Certification(
        trainee_id=primary_trainee.id,
        course_id=course_1.id,
        certificate_number="SP-CERT-2025-99812",
        issue_date="2025-11-25",
        status="ISSUED"
    )
    db.add(primary_cert)

    # Trainee skills
    primary_skills = ["JavaScript", "React", "Python", "SQL", "REST APIs", "Git", "HTML/CSS"]
    for sk in primary_skills:
        db.add(TraineeSkill(
            trainee_id=primary_trainee.id,
            skill_name=sk,
            proficiency_level="ADVANCED" if sk in ["JavaScript", "React", "Python"] else "INTERMEDIATE",
            is_verified=True
        ))

    # Employment Record
    primary_emp = EmploymentRecord(
        trainee_id=primary_trainee.id,
        employer_id=employers_list[0].id,  # TCS
        employer_name="Tata Consultancy Services",
        job_title="Associate Software Engineer",
        joining_date="2025-12-15",
        starting_salary=24000.0,
        current_salary=32000.0,
        location_city="Pune",
        location_state="Maharashtra",
        employment_type="FULL_TIME",
        status="EMPLOYED",
        verification_status="VERIFIED",
        verified_at=datetime.utcnow() - timedelta(days=90),
        confidence_score=0.96
    )
    db.add(primary_emp)
    db.flush()

    # Verification record
    db.add(EmployerVerification(
        employment_record_id=primary_emp.id,
        employer_id=employers_list[0].id,
        verified_by_user_id=employer_user.id,
        status="VERIFIED",
        notes="Verified active employment under Cloud Digital practice with outstanding performance.",
        verified_salary=32000.0,
        verified_joining_date="2025-12-15",
        verified_job_title="Associate Software Engineer"
    ))

    # Wage history for Aarav
    db.add(WageHistory(
        trainee_id=primary_trainee.id,
        employment_record_id=primary_emp.id,
        effective_date="2025-12-15",
        salary_amount=24000.0,
        growth_pct_since_starting=0.0,
        notes="Initial Placement Joining"
    ))
    db.add(WageHistory(
        trainee_id=primary_trainee.id,
        employment_record_id=primary_emp.id,
        effective_date="2026-03-15",
        salary_amount=28000.0,
        growth_pct_since_starting=16.7,
        notes="3-Month Probation Completion Bonus"
    ))
    db.add(WageHistory(
        trainee_id=primary_trainee.id,
        employment_record_id=primary_emp.id,
        effective_date="2026-06-15",
        salary_amount=32000.0,
        growth_pct_since_starting=33.3,
        notes="6-Month Longitudinal Performance Hike"
    ))

    # Follow-ups for Aarav
    db.add(Followup(
        trainee_id=primary_trainee.id,
        checkpoint="30_DAYS",
        status="RESPONDED",
        scheduled_date="2025-12-25",
        sent_at=datetime.utcnow() - timedelta(days=220),
        responded_at=datetime.utcnow() - timedelta(days=219),
        response_data={"employed": True, "employer": "TCS", "salary": 24000, "satisfaction": 5},
        channel="WHATSAPP_MOCK",
        sent_message="Hello Aarav! 30 days since certification: confirmed employment at Tata Consultancy Services."
    ))
    db.add(Followup(
        trainee_id=primary_trainee.id,
        checkpoint="90_DAYS",
        status="RESPONDED",
        scheduled_date="2026-02-25",
        sent_at=datetime.utcnow() - timedelta(days=160),
        responded_at=datetime.utcnow() - timedelta(days=159),
        response_data={"employed": True, "employer": "TCS", "salary": 28000, "satisfaction": 5},
        channel="WHATSAPP_MOCK",
        sent_message="Hi Aarav! 90-day check-in: confirmed salary progression to ₹28,000/mo."
    ))
    db.add(Followup(
        trainee_id=primary_trainee.id,
        checkpoint="6_MONTHS",
        status="RESPONDED",
        scheduled_date="2026-05-25",
        sent_at=datetime.utcnow() - timedelta(days=70),
        responded_at=datetime.utcnow() - timedelta(days=69),
        response_data={"employed": True, "same_employer": True, "salary": 32000, "satisfaction": 5},
        channel="WHATSAPP_MOCK",
        sent_message="Greetings Aarav! 6-Month retention confirmed with 33.3% wage growth."
    ))
    db.add(Followup(
        trainee_id=primary_trainee.id,
        checkpoint="12_MONTHS",
        status="SCHEDULED",
        scheduled_date="2026-11-25",
        channel="WHATSAPP_MOCK",
        sent_message="Scheduled: 1-Year longitudinal career progression review."
    ))

    # AI Skill Gap Analysis for Aarav
    db.add(SkillGapAnalysis(
        trainee_id=primary_trainee.id,
        target_role="Full Stack Developer",
        skill_gap_score=22.5,
        matched_skills_json=[
            {"skill": "JavaScript", "match_pct": 95, "proficiency": "ADVANCED"},
            {"skill": "React", "match_pct": 92, "proficiency": "ADVANCED"},
            {"skill": "Python", "match_pct": 88, "proficiency": "ADVANCED"},
            {"skill": "SQL", "match_pct": 84, "proficiency": "INTERMEDIATE"},
            {"skill": "REST APIs", "match_pct": 90, "proficiency": "ADVANCED"},
            {"skill": "Git", "match_pct": 94, "proficiency": "ADVANCED"},
            {"skill": "HTML/CSS", "match_pct": 92, "proficiency": "ADVANCED"}
        ],
        missing_skills_json=["Docker", "AWS", "CI/CD"],
        confidence_score=0.92,
        recommended_skills_json=[
            "Focus on mastering high-priority target competencies: Docker, AWS, CI/CD.",
            "Containerization & Microservices with Docker",
            "AWS Cloud Practitioner for Developers"
        ]
    ))

    # -------------------------------------------------------------
    # 50+ Additional Realistic Trainees across India
    # -------------------------------------------------------------
    print("👥 Seeding 50+ Trainees with Longitudinal Journeys...")
    indian_names = [
        ("Pooja Patel", "Female", "B.Sc IT", "Ahmedabad", "Gujarat"),
        ("Rohan Verma", "Male", "B.Tech Mech", "Pune", "Maharashtra"),
        ("Ananya Iyer", "Female", "BCA", "Chennai", "Tamil Nadu"),
        ("Vikram Singh", "Male", "Diploma Electronics", "Jaipur", "Rajasthan"),
        ("Meera Nair", "Female", "B.Sc Computer Science", "Kochi", "Kerala"),
        ("Aditya Kulkarni", "Male", "B.E IT", "Pune", "Maharashtra"),
        ("Neha Gupta", "Female", "B.Com / MCA", "Lucknow", "Uttar Pradesh"),
        ("Siddharth Menon", "Male", "B.Tech CS", "Bengaluru Urban", "Karnataka"),
        ("Priyanka Roy", "Female", "B.Sc Data Science", "Kolkata", "West Bengal"),
        ("Karthik Reddy", "Male", "B.Tech ECE", "Hyderabad", "Telangana"),
        ("Divya Balakrishnan", "Female", "B.Tech IT", "Chennai", "Tamil Nadu"),
        ("Arjun Deshpande", "Male", "Diploma Computer Engg", "Nagpur", "Maharashtra"),
        ("Sneha Joshi", "Female", "BCA", "Nashik", "Maharashtra"),
        ("Manish Kumar", "Male", "B.Sc Physics", "Patna", "Bihar"),
        ("Ritu Sharma", "Female", "MCA", "Chandigarh", "Punjab"),
        ("Harish Pillai", "Male", "B.E Mechanical", "Thiruvananthapuram", "Kerala"),
        ("Tanvi Chawla", "Female", "B.Tech CS", "Delhi", "Delhi"),
        ("Gaurav Bansal", "Male", "BCA", "Indore", "Madhya Pradesh"),
        ("Deepika Sen", "Female", "B.Sc IT", "Bhubaneswar", "Odisha"),
        ("Varun Hegde", "Male", "B.Tech CS", "Mangaluru", "Karnataka"),
        ("Shreya Bhattacharya", "Female", "B.Sc Stats", "Kolkata", "West Bengal"),
        ("Nikhil Tiwari", "Male", "Diploma Electrical", "Varanasi", "Uttar Pradesh"),
        ("Anjali Saxena", "Female", "BCA", "Bhopal", "Madhya Pradesh"),
        ("Kunal Mehta", "Male", "B.Tech IT", "Mumbai", "Maharashtra"),
        ("Swati Rao", "Female", "B.E Electronics", "Bengaluru Urban", "Karnataka"),
        ("Abhishek Mishra", "Male", "B.Sc Computer Science", "Ranchi", "Jharkhand"),
        ("Pallavi Deshmukh", "Female", "B.Tech CS", "Pune", "Maharashtra"),
        ("Rahul Nambiar", "Male", "Diploma Mech", "Kozhikode", "Kerala"),
        ("Isha Agarwal", "Female", "B.Com / IT Skills", "Agra", "Uttar Pradesh"),
        ("Saurabh Patil", "Male", "B.E Civil", "Kolhapur", "Maharashtra"),
        ("Kavya Sundaram", "Female", "BCA", "Madurai", "Tamil Nadu"),
        ("Akash Pandey", "Male", "B.Tech CS", "Kanpur", "Uttar Pradesh"),
        ("Monika Sethi", "Female", "B.Sc IT", "Dehradun", "Uttarakhand"),
        ("Sanjay Rathore", "Male", "Diploma Automobile", "Udaipur", "Rajasthan"),
        ("Aparna Ganesan", "Female", "B.Tech ECE", "Coimbatore", "Tamil Nadu"),
        ("Vivek Dubey", "Male", "BCA", "Prayagraj", "Uttar Pradesh"),
        ("Nandini Varma", "Female", "B.Sc IT", "Vadodara", "Gujarat"),
        ("Prateek Jain", "Male", "B.Tech CS", "Surat", "Gujarat"),
        ("Bhavna Chauhan", "Female", "B.A / Data Entry", "Meerut", "Uttar Pradesh"),
        ("Dinesh Gowda", "Male", "Diploma Mechanical", "Mysuru", "Karnataka"),
        ("Archana Prabhu", "Female", "B.Tech IT", "Bengaluru Urban", "Karnataka"),
        ("Mohit Aggarwal", "Male", "BCA", "Gurugram", "Haryana"),
        ("Sunita Mahajan", "Female", "B.Sc Computer Science", "Amravati", "Maharashtra"),
        ("Tushar Gaikwad", "Male", "B.Tech Electrical", "Aurangabad", "Maharashtra"),
        ("Vidya Subramanian", "Female", "MCA", "Tiruchirappalli", "Tamil Nadu"),
        ("Yash Singhal", "Male", "B.Tech CS", "Noida", "Uttar Pradesh"),
        ("Kiran Nayak", "Female", "BCA", "Hubballi", "Karnataka"),
        ("Omkar Sawant", "Male", "Diploma IT", "Goa", "Goa"),
        ("Jaspreet Kaur", "Female", "B.Tech IT", "Amritsar", "Punjab"),
        ("Naveen Choudhary", "Male", "B.Sc Math", "Jodhpur", "Rajasthan")
    ]

    for idx, (name, gender, edu, dist, st) in enumerate(indian_names, start=2):
        sp_id = f"SP-2026-{idx + 300:06d}"
        clean_email = f"{name.lower().replace(' ', '').replace('/', '')}{idx}@trainee.skillpulse.demo"

        # User
        u = User(
            email=clean_email,
            hashed_password=hashed_pwd,
            role="TRAINEE",
            full_name=name,
            phone=f"+91 {98000 + idx:05d} {10000 + idx:05d}",
            is_active=True
        )
        db.add(u)
        db.flush()

        # Trainee
        t = Trainee(
            user_id=u.id,
            skillpulse_id=sp_id,
            full_name=name,
            email=clean_email,
            phone=u.phone,
            state=st,
            district=dist,
            education=edu,
            gender=gender,
            consent_given=True
        )
        db.add(t)
        db.flush()

        # Consent
        db.add(Consent(
            user_id=u.id,
            trainee_id=t.id,
            consent_status=True,
            consent_version="v1.0",
            consent_text="I consent to SkillPulse tracking my training and employment outcomes."
        ))

        # Assign Course & Provider
        c_idx = (idx - 2) % len(courses_list)
        assigned_course = courses_list[c_idx]
        assigned_provider = providers_list[c_idx % len(providers_list)]

        # Training Record
        score = 65.0 + ((idx * 7) % 32)
        is_completed = score >= 55.0

        tr_rec = TrainingRecord(
            trainee_id=t.id,
            course_id=assigned_course.id,
            provider_id=assigned_provider.id,
            cohort_id=f"COHORT-2025-Q{((idx % 2) + 3)}",
            start_date="2025-08-15" if idx % 2 == 0 else "2025-10-01",
            end_date="2025-12-10" if idx % 2 == 0 else "2026-01-20",
            completion_status="COMPLETED" if is_completed else "IN_PROGRESS",
            attendance_pct=round(85.0 + ((idx * 3) % 15), 1)
        )
        db.add(tr_rec)
        db.flush()

        # Assessment
        db.add(Assessment(
            training_record_id=tr_rec.id,
            trainee_id=t.id,
            assessment_name=f"{assigned_course.course_name} Standardized Competency Evaluation",
            score=score,
            max_score=100.0,
            pass_status=score >= 60.0,
            date_taken="2025-12-12" if idx % 2 == 0 else "2026-01-22"
        ))

        # Certification
        if score >= 60.0:
            db.add(Certification(
                trainee_id=t.id,
                course_id=assigned_course.id,
                certificate_number=f"SP-CERT-2026-{idx:05d}",
                issue_date="2025-12-15" if idx % 2 == 0 else "2026-01-25",
                status="ISSUED"
            ))

        # Skills
        course_skills = assigned_course.required_skills or ["Technical Analysis", "Problem Solving"]
        for sk_name in course_skills:
            db.add(TraineeSkill(
                trainee_id=t.id,
                skill_name=sk_name,
                proficiency_level="ADVANCED" if score > 82 else "INTERMEDIATE",
                is_verified=True
            ))

        # Employment status (82% employed, 14% searching, 4% not looking)
        is_employed = (idx % 6 != 0)
        is_searching = not is_employed and (idx % 2 == 0)

        emp_status = "EMPLOYED" if is_employed else ("SEARCHING" if is_searching else "NOT_LOOKING")
        assigned_employer = employers_list[idx % len(employers_list)]

        start_sal = 18000.0 + ((idx * 1500) % 22000)
        curr_sal = start_sal * (1.25 if idx % 3 == 0 else (1.35 if idx % 2 == 0 else 1.15)) if is_employed else 0.0

        is_verified = (idx % 4 != 0)  # Some pending for employer verification demo
        v_status = "VERIFIED" if (is_employed and is_verified) else ("PENDING" if is_employed else "NOT_APPLICABLE")

        emp_rec = EmploymentRecord(
            trainee_id=t.id,
            employer_id=assigned_employer.id if is_employed else None,
            employer_name=assigned_employer.company_name if is_employed else None,
            job_title=f"Junior {assigned_course.domain} Associate" if is_employed else None,
            joining_date="2026-01-10" if is_employed else None,
            starting_salary=start_sal if is_employed else None,
            current_salary=round(curr_sal, 0) if is_employed else None,
            location_city=dist,
            location_state=st,
            employment_type="FULL_TIME",
            status=emp_status,
            verification_status=v_status,
            verified_at=datetime.utcnow() - timedelta(days=40) if v_status == "VERIFIED" else None,
            confidence_score=0.94 if v_status == "VERIFIED" else 0.72
        )
        db.add(emp_rec)
        db.flush()

        # Employer verification audit if verified
        if v_status == "VERIFIED":
            db.add(EmployerVerification(
                employment_record_id=emp_rec.id,
                employer_id=assigned_employer.id,
                verified_by_user_id=employer_user.id,
                status="VERIFIED",
                notes="Verified active employment through quarterly payroll confirmation.",
                verified_salary=curr_sal,
                verified_joining_date="2026-01-10",
                verified_job_title=emp_rec.job_title
            ))

        # Wage history
        if is_employed:
            db.add(WageHistory(
                trainee_id=t.id,
                employment_record_id=emp_rec.id,
                effective_date="2026-01-10",
                salary_amount=start_sal,
                growth_pct_since_starting=0.0,
                notes="Initial Joining"
            ))
            if curr_sal > start_sal:
                growth_calc = round(((curr_sal - start_sal) / start_sal) * 100.0, 1)
                db.add(WageHistory(
                    trainee_id=t.id,
                    employment_record_id=emp_rec.id,
                    effective_date="2026-06-15",
                    salary_amount=round(curr_sal, 0),
                    growth_pct_since_starting=growth_calc,
                    notes="6-Month Performance Increment"
                ))

        # Follow-ups (30d, 90d, 6m, 12m)
        fup_checkpoints = [
            ("30_DAYS", "2026-02-15", "RESPONDED"),
            ("90_DAYS", "2026-04-15", "RESPONDED" if idx % 5 != 0 else "SENT"),
            ("6_MONTHS", "2026-07-15", "RESPONDED" if idx % 4 != 0 else "SCHEDULED"),
            ("12_MONTHS", "2027-01-15", "SCHEDULED")
        ]
        for cp_name, cp_date, cp_st in fup_checkpoints:
            db.add(Followup(
                trainee_id=t.id,
                checkpoint=cp_name,
                status=cp_st,
                scheduled_date=cp_date,
                sent_at=datetime.utcnow() - timedelta(days=60) if cp_st != "SCHEDULED" else None,
                responded_at=datetime.utcnow() - timedelta(days=58) if cp_st == "RESPONDED" else None,
                response_data={"employed": is_employed, "current_salary": curr_sal} if cp_st == "RESPONDED" else None,
                channel="WHATSAPP_MOCK",
                sent_message=f"[Mock Follow-up] Checkpoint {cp_name} for {t.full_name}"
            ))

        # AI Skill Gap Analysis
        gap_score = max(12.0, min(48.0, round(50.0 - (score * 0.4), 1)))
        db.add(SkillGapAnalysis(
            trainee_id=t.id,
            target_role=assigned_course.target_roles[0] if assigned_course.target_roles else "Technical Specialist",
            skill_gap_score=gap_score,
            matched_skills_json=[{"skill": sk, "match_pct": int(score * 0.95), "proficiency": "INTERMEDIATE"} for sk in course_skills[:3]],
            missing_skills_json=["Advanced Cloud Architecture", "CI/CD Orchestration"],
            confidence_score=0.88,
            recommended_skills_json=["Complete intermediate cloud projects", "Practice unit testing with mock frameworks"]
        ))

    db.commit()

    # --- NEXTUP: Seed Target Jobs & Job Requirements ---
    print("Seeding Target Jobs & Job Requirements...")
    job_specs = [
        ("Full Stack Developer", "JOB-FS-001", "Information Technology",
         "Designs and develops responsive web applications end-to-end.",
         480000, 1200000, "HIGH",
         [("JavaScript", 0.9, True), ("React", 0.85, True), ("Python", 0.75, True),
          ("SQL", 0.75, True), ("REST APIs", 0.8, True), ("Git", 0.7, False)]),
        ("Data Analyst", "JOB-DA-001", "Data Science & AI",
         "Analyses structured datasets to derive actionable business insights.",
         420000, 960000, "HIGH",
         [("Python", 0.85, True), ("SQL", 0.9, True), ("Excel", 0.8, True),
          ("Power BI", 0.75, True), ("Statistics", 0.7, False)]),
        ("Cloud & DevOps Engineer", "JOB-CD-001", "Cloud Infrastructure",
         "Manages cloud infrastructure, CI/CD pipelines, and container orchestration.",
         600000, 1500000, "CRITICAL",
         [("Docker", 0.85, True), ("AWS", 0.85, True), ("Linux", 0.9, True),
          ("Kubernetes", 0.8, False), ("Terraform", 0.7, False)]),
        ("Industrial IoT Specialist", "JOB-IOT-001", "Industrial Electronics",
         "Designs and deploys connected industrial automation systems.",
         360000, 840000, "MODERATE",
         [("C/C++", 0.8, True), ("Embedded Systems", 0.85, True),
          ("MQTT", 0.75, True), ("PLC Programming", 0.7, False)]),
        ("Healthcare Data Coordinator", "JOB-HC-001", "Healthcare Technology",
         "Manages EHR data workflows and clinical data compliance.",
         300000, 600000, "MODERATE",
         [("Medical Terminology", 0.85, True), ("EHR Systems", 0.85, True),
          ("Healthcare Compliance & HIPAA", 0.85, True), ("Excel", 0.75, False)]),
    ]
    for title, code, domain, desc, sal_min, sal_max, demand, skill_reqs in job_specs:
        job = Job(
            title=title, code=code, domain=domain, description=desc,
            salary_range_min=sal_min, salary_range_max=sal_max,
            demand_level=demand, is_active=True
        )
        db.add(job)
        db.flush()
        for sk_name, weight, mandatory in skill_reqs:
            db.add(JobRequirement(
                job_id=job.id, skill_name=sk_name,
                importance_weight=weight, is_mandatory=mandatory,
            ))
    db.commit()

    # --- NEXTUP: Seed Demo Intervention for Primary Trainee ---
    print("Seeding demo Intervention for primary trainee...")
    demo_intervention = Intervention(
        trainee_id=primary_trainee.id,
        risk_level="MEDIUM",
        risk_score=52.0,
        trigger_reason="Moderate placement risk with Docker and AWS skill gaps detected",
        title="Skill Enhancement & Job Readiness Program",
        description=(
            "Trainee has moderate placement risk. Targeted skill enhancement "
            "and increased job search activity will improve outcomes."
        ),
        target_skills=["Docker", "AWS", "TypeScript"],
        recommended_actions=[
            "Priority skill modules to complete: Docker, AWS, TypeScript",
            "Complete 2 missing skill modules identified in skill gap analysis",
            "Build or update online portfolio/GitHub profile",
            "Submit at least 3 job applications per week",
            "Seek mentorship from placed alumni",
        ],
        status="IN_PROGRESS",
    )
    db.add(demo_intervention)
    db.commit()

    print("NEXTUP Seed completed! (SIH26135 | Team Lumora)")
    print(f"Summary:")
    print(f"   - Users: {db.query(User).count()}")
    print(f"   - Trainees: {db.query(Trainee).count()}")
    print(f"   - Providers: {db.query(Provider).count()}")
    print(f"   - Employers: {db.query(Employer).count()}")
    print(f"   - Courses: {db.query(Course).count()}")
    print(f"   - Jobs: {db.query(Job).count()}")
    print(f"   - Certifications: {db.query(Certification).count()}")
    print(f"   - Employment Records: {db.query(EmploymentRecord).count()}")
    print(f"   - Follow-ups: {db.query(Followup).count()}")
    print(f"   - Interventions: {db.query(Intervention).count()}")
    print(f"")
    print(f"   DEMO CREDENTIALS (password for all: {DEMO_PWD})")
    print(f"     Trainee:  trainee@nextup.demo")
    print(f"     Provider: provider@nextup.demo")
    print(f"     Employer: employer@nextup.demo")
    print(f"     Admin:    admin@nextup.demo")
    print(f"")
    print(f"   NOTE: All data is DEMO/SYNTHETIC for SIH26135 demonstration only.")
    db.close()

if __name__ == "__main__":
    seed_database()

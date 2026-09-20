# NXTUP — AI-Powered Longitudinal Skilling Outcome Platform

> **Smart India Hackathon 2026 (SIH 2026)**  
> **Problem ID:** SIH26135  
> **Team:** Team Lumora  
> **Mission:** *"Bridging India's Post-Skilling Data Gap Through Longitudinal Outcome Tracking & AI Early-Warning Interventions."*

---

## 🎯 Executive Summary

Across national skilling ecosystems (such as PMKVY, DGT, and State Skill Missions), tracking often terminates upon certification issuance. This creates a critical blindspot: **institutions lack verifiable data on whether graduates secure sustained employment, retain their jobs after 6–12 months, or achieve real wage progression.**

**NXTUP** solves this systemic challenge with an integrated, production-ready platform featuring:
1. **Persistent Unified Trainee Identifier (`NXT-YYYY-XXXXXX`)** — A privacy-preserving national skilling ID that connects training, certification, employer verification, and career progression across a trainee's entire lifecycle.
2. **Machine Learning Placement Risk Prediction** — A scikit-learn classification pipeline (RandomForest / GradientBoosting) that identifies at-risk trainees before course completion based on attendance, assessment scores, and skill gap telemetry.
3. **Automated Remedial Intervention Engine** — Dynamically recommends targeted interventions (Mock Interviews, Bridge Courses, 1-on-1 Mentorship) with actionable sprint checklists.
4. **Dual-Stakeholder Verification Workflow** — Tamper-resistant employment reporting where hiring employers cryptographically verify job titles, joining dates, and starting compensation.
5. **DPDP Act & GDPR-Compliant Consent Framework** — Explicit, versioned, timestamped, purpose-bound, and revocable consent capture prior to longitudinal tracking.
6. **Macro Policy Analytics Engine** — Real-time SQL aggregation for policymakers tracking 6-month retention rates, median wage growth (%), and geographic district heatmaps.

---

## ⚡ Implementation Status: Live vs Planned Roadmap

To ensure academic and competition integrity, NXTUP clearly delineates **live/implemented** capabilities from **future planned** roadmap integrations:

| Capability / Module | Status | Technical Implementation Details |
| :--- | :---: | :--- |
| **Persistent NXTUP ID (`NXT-YYYY-XXXXXX`)** | <mark>**LIVE**</mark> | Deterministic cryptographic generator with checksum and database uniqueness constraints. |
| **ML Placement Risk Prediction Engine** | <mark>**LIVE**</mark> | Scikit-learn classification pipeline trained on structured skilling telemetry with explainable risk drivers. |
| **Personalized Remedial Interventions** | <mark>**LIVE**</mark> | Rule-based & ML-assisted intervention generator with full lifecycle state management (`RECOMMENDED` → `IN_PROGRESS` → `COMPLETED`). |
| **Dual-Party Employer Verification** | <mark>**LIVE**</mark> | Trainee self-report followed by employer payroll verification loop with confidence scoring. |
| **Longitudinal 3/6/12-Month Retention Tracking** | <mark>**LIVE**</mark> | Automated check-in notification framework and wage trajectory computation (`((Current - Base) / Base) * 100`). |
| **DPDP Act Explicit Consent Lifecycle** | <mark>**LIVE**</mark> | Auditable consent capture with client IP, timestamping, versioning, and instant revocation capability. |
| **Macro Policy & District Analytics** | <mark>**LIVE**</mark> | PostgreSQL multi-table aggregation across batches, sectors, providers, and states. |
| **DigiLocker / Aadhaar Vault Integration** | *PLANNED* | Direct India Stack API integration pending government sandbox credentials. |
| **EPFO / ESIC Real-time Contribution Sync** | *PLANNED* | Statutory PF/ESI automated employment validation pipeline for institutional scale. |

---

## 🏛 System Architecture

```
nxtup/
├── backend/
│   ├── alembic/                 # Database schema migrations
│   ├── app/
│   │   ├── ai/                  # AI service (LLM skill-gap detection with resilient fallback)
│   │   ├── api/                 # REST API endpoints (/api)
│   │   │   ├── auth.py          # JWT authentication & registration
│   │   │   ├── consent.py       # DPDP consent lifecycle & audit trail
│   │   │   ├── trainee.py       # Trainee profile, milestones, & wage progression
│   │   │   ├── provider.py      # Batch management & CSV trainee ingestion
│   │   │   ├── employer.py      # Verification queue & talent search
│   │   │   ├── employment.py    # Trainee job reporting
│   │   │   ├── followups.py     # 30d/90d/6m/12m milestone scheduler
│   │   │   ├── ml.py            # ML placement risk prediction & intervention endpoints
│   │   │   ├── jobs.py          # Industry target jobs catalogue & requirements
│   │   │   ├── analytics.py     # Macro policy outcome aggregations
│   │   │   └── router.py        # Central FastAPI router
│   │   ├── ml/                  # Machine Learning pipeline
│   │   │   ├── pipeline_train.py          # Training pipeline (RandomForest/LogisticRegression)
│   │   │   ├── risk_service.py            # Real-time placement risk inference engine
│   │   │   ├── recommendation_service.py  # Personalized intervention prescriptive service
│   │   │   ├── retraining_service.py      # Automated retraining trigger on verified data
│   │   │   └── data/                      # Model artifact (.joblib), metadata, synthetic dataset
│   │   ├── models/              # SQLAlchemy relational models (User, Trainee, Job, Intervention, etc.)
│   │   ├── schemas/             # Pydantic validation schemas
│   │   ├── services/            # Background notification & CSV import services
│   │   ├── utils/               # ID generator (`NXT-YYYY-XXXXXX`), skill normalizer, audit logger
│   │   ├── config.py            # Environment configuration & SIH metadata
│   │   ├── database.py          # Session factory & SQLite/PostgreSQL switcher
│   │   └── main.py              # FastAPI application entrypoint
│   ├── tests/                   # 20+ automated pytest test suites
│   ├── requirements.txt         # Backend Python dependencies
│   └── Dockerfile               # Container build definition
│
├── frontend/
│   ├── src/
│   │   ├── components/          # PlacementRiskCard, TraineeJourneyTracker, SkillGapCard, Recharts
│   │   ├── contexts/            # AuthContext (token/user/NXTUP ID management), ToastContext
│   │   ├── layouts/             # DashboardLayout, AdminLayout, PublicLayout
│   │   ├── pages/               # LandingPage, LoginPage, RegisterPage, ConsentPage, Dashboards
│   │   └── services/            # Axios API client (/api)
│   ├── package.json
│   └── vite.config.js
│
├── docker-compose.yml           # Full-stack container orchestration
├── .env.example                 # Environment variable template
└── README.md                    # System documentation
```

---

## 🛠 Technology Stack

- **Backend Framework:** FastAPI (Python 3.10+) with Pydantic v2 data validation
- **Relational Database:** PostgreSQL (Production / Docker) with automatic fallback to SQLite (Local Dev)
- **Machine Learning Stack:** Scikit-learn, NumPy, Pandas, Joblib
- **Frontend Architecture:** React 18, Vite, Tailwind CSS, Recharts, Lucide Icons, Axios
- **Authentication & Security:** JWT (JSON Web Tokens), OAuth2 password bearer, Passlib (bcrypt), DPDP audit trail
- **Quality Assurance:** Pytest, FastAPI TestClient, 100% automated test pass rate

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.10+
- Node.js 18+ and npm
- (Optional) PostgreSQL 14+ or Docker

### 2. Backend Setup
```bash
cd backend
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt

# Run database seed (generates target jobs, courses, and demo users)
python -m database.seed

# Start the API server
uvicorn app.main:app --reload --port 8000
```
Backend API will be live at: `http://localhost:8000`  
Interactive Swagger Documentation: `http://localhost:8000/docs`

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Frontend Web Portal will be live at: `http://localhost:5173`

---

## 🔑 SIH 2026 Evaluation Demo Credentials

The application includes 1-click quick-fill presets on the Login page for evaluating all four stakeholder personas:

| Persona / Role | Email | Password | Primary Capabilities |
| :--- | :--- | :--- | :--- |
| **🎓 Trainee** | `trainee@nextup.demo` | `NextUp@Demo2026!` | Unified NXTUP ID, AI Placement Risk Score, Personalized Remedial Interventions, Wage Progression Tracker. |
| **🏫 Training Provider** | `provider@nextup.demo` | `NextUp@Demo2026!` | Batch outcome rosters, cohort risk analytics, course completion metrics, bulk CSV trainee ingestion. |
| **💼 Employer** | `employer@nextup.demo` | `NextUp@Demo2026!` | Verification queue for reported hires, salary/designation validation, consenting graduate candidate talent pool. |
| **🏛️ Govt / Admin** | `pn2552007@gmail.com` | `[Configured Administrator Password]` | Macro outcome metrics (6-month retention %, wage growth %), ML model monitoring, district & sector impact rankings. |

---

## 🧪 Automated Testing

NXTUP includes an exhaustive automated test suite covering all authentication flows, ID generation formats, DPDP consent lifecycle, ML risk inference, and target jobs:

```bash
cd backend
python -m pytest tests/ -v
```

**Test Coverage Summary:**
- `test_nextup_features.py`: Validates `NXT-YYYY-XXXXXX` persistent ID format, `/api/ml/predict-risk`, `/api/ml/model-info`, `/api/ml/recommend-intervention`, and `/api/jobs`.
- `test_trainee_and_consent.py`: Tests trainee registration, persistent ID assignment, DPDP consent grant & revocation.
- `test_auth_and_rbac.py`: Role-based access control across Trainee, Provider, Employer, and Admin scopes.
- `test_employment_and_verification.py`: Employment reporting, employer verification lifecycle, and confidence score calculation.
- `test_analytics.py`: Dedicated macro analytics aggregation queries.
- `test_followups.py`: Longitudinal 30d/90d/6m/12m milestone scheduler.
- `test_provider_and_skills.py`: Skill normalizer and course batch creation.

---

## 👥 Team Lumora (SIH 2026)
- **Problem ID:** SIH26135
- **Category:** Software / National Skilling & Workforce Development
- **Project:** NXTUP Longitudinal Skilling Outcome Platform

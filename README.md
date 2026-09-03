# SkillPulse — AI-Powered Longitudinal Skilling Outcome Tracking Platform

> **"Track the journey from vocational skilling to sustained career impact."**

SkillPulse is a production-grade, full-stack enterprise web application engineered to bridge the critical visibility gap in national and institutional skilling initiatives. It tracks trainees longitudinally through every stage of their career progression: institutional training, certifications, verified employer placements, 6-month and 12-month retention, and wage growth.

---

## 🌟 Core Platform Principles

1. **Zero-Data Startup Guarantee**: Starts with zero synthetic records. Every dashboard metric, trendline, and aggregate chart derives directly from authenticated SQL database records.
2. **Persistent SkillPulse ID (`SP-XXXXXXXX`)**: Generates cryptographically secure, non-sequential, 8-character identifiers (e.g., `SP-4K9W2B8Z`) that act as a public reference without exposing PII (phone/email).
3. **Explicit Consent & DPDP Compliance**: Trainee consent is legally versioned, timestamped, purpose-bound, auditable, and revocable. Candidate discovery and longitudinal follow-ups are restricted to consenting individuals.
4. **External Generative AI Skill-Gap Engine**: Powered by Groq LLaMA models (e.g., `llama-3.3-70b-versatile`) via `AIClient` and `AIService`. Uses structured prompts and Pydantic schema validation (`AIAnalysisOutput`). Gracefully handles unconfigured API keys without crashing or fabricating fake skills.
5. **Dual-Stakeholder Verification Workflow**: Employment reported by trainees undergoes confirmation by employers with automated confidence scoring based on role, joining date, and compensation matching.
6. **Dedicated Macro Analytics Engine**: Specialized `/api/analytics` endpoints compute macro employment rates, retention rates, wage growth distributions, and geographic disparity indices using SQL joins and aggregations.
7. **Database Migrations via Alembic**: Full DDL schema management with migrations tracked and applied sequentially (`alembic upgrade head`).

---

## 🏛 System Architecture

```
skillpulse/
├── backend/
│   ├── alembic/                 # Alembic migration environment & revisions
│   │   └── versions/            # Versioned schema migrations
│   ├── app/
│   │   ├── ai/
│   │   │   ├── ai_client.py     # Resilient Groq LLaMA AI client with HTTP fallback
│   │   │   └── ai_service.py    # Structured prompt engineering & Pydantic validation
│   │   ├── api/
│   │   │   ├── auth.py          # JWT authentication, registration, & password hashing
│   │   │   ├── consent.py       # DPDP consent lifecycle & audit trail
│   │   │   ├── trainee.py       # Trainee profile, skills, & wage progression
│   │   │   ├── provider.py      # Course creation, batch management, & CSV roster import
│   │   │   ├── employer.py      # Verification requests & candidate talent discovery
│   │   │   ├── employment.py    # Trainee employment reporting & wage initialization
│   │   │   ├── followups.py     # 30d/90d/6m/12m milestone scheduling & response handling
│   │   │   ├── analytics.py     # Dedicated SQL aggregation & macro analytics
│   │   │   ├── ai.py            # AI skill-gap evaluation endpoints
│   │   │   └── router.py        # Central API router (/api)
│   │   ├── auth/
│   │   │   └── jwt_handler.py   # JWT token generation, verification, & RBAC dependencies
│   │   ├── models/
│   │   │   └── models.py        # 17 SQLAlchemy relational models
│   │   ├── schemas/
│   │   │   └── schemas.py       # Pydantic v2 validation models
│   │   ├── services/
│   │   │   ├── notification_service.py  # Longitudinal communication abstraction
│   │   │   └── csv_import_service.py    # CSV batch roster ingestion with ID generation
│   │   ├── utils/
│   │   │   ├── audit.py         # Persistent audit log persistence
│   │   │   ├── id_generator.py  # Cryptographic SP-XXXXXXXX generator
│   │   │   └── skill_normalizer.py # Canonical skill normalization & deduplication
│   │   ├── config.py            # Pydantic BaseSettings (.env loader)
│   │   ├── database.py          # SQLAlchemy engine & session factory
│   │   └── main.py              # FastAPI application entrypoint
│   ├── tests/                   # Automated pytest suite
│   ├── alembic.ini              # Alembic configuration
│   ├── requirements.txt         # Backend Python dependencies
│   └── Dockerfile               # Production container image
│
├── frontend/
│   ├── src/
│   │   ├── components/          # Reusable UI components & Recharts visualizations
│   │   ├── contexts/            # React AuthContext & ToastContext
│   │   ├── layouts/             # DashboardLayout & PublicLayout
│   │   ├── pages/               # Trainee, Provider, Employer, Admin, Auth pages
│   │   └── services/            # Axios API client (/api)
│   ├── package.json
│   └── vite.config.js
│
├── docker-compose.yml           # Multi-container orchestration (DB, API, Frontend)
├── .env.example                 # Environment configuration template
└── README.md                    # System documentation
```

---

## 🛠 Technology Stack

- **Backend**: Python 3.14 / FastAPI, SQLAlchemy 2.0, Pydantic v2, Alembic, Passlib (bcrypt), Python-Jose (JWT).
- **AI Integration**: Groq API (`groq` SDK / LLaMA 3.3 70B Versatile), external HTTP fallback, Pydantic structured output validation.
- **Frontend**: React 18, Vite, Tailwind CSS, Lucide Icons, Recharts, Axios.
- **Database**: PostgreSQL (Production / Docker) or SQLite (Local Development).
- **Testing**: Pytest, FastAPI TestClient (`httpx`).

---

## ⚙️ Environment Variables

Create a `.env` file in the project root based on `.env.example`:

```env
DATABASE_URL=postgresql://skillpulse:skillpulse@localhost:5432/skillpulse
JWT_SECRET=your-secure-random-jwt-secret-key-at-least-32-chars
AI_PROVIDER=groq
GROQ_API_KEY=your-groq-api-key-here
AI_API_KEY=your-groq-api-key-here
AI_MODEL=llama-3.3-70b-versatile
```

*Note: If `GROQ_API_KEY` is not provided, the platform functions normally, and the AI service returns clear configuration notices without crashing.*

---

## 🚀 Quickstart Guide

### Option 1: Docker Compose (Recommended)

Run the complete multi-container stack with PostgreSQL, FastAPI backend, and React frontend:

```bash
docker-compose up --build
```

- **Frontend Portal**: `http://localhost:5173`
- **Backend API Docs**: `http://localhost:8000/docs`
- **Database**: `localhost:5432`

The backend container runs database migrations (`alembic upgrade head`) automatically on startup.

---

### Option 2: Local Development

#### 1. Backend Setup

```bash
cd backend

# Create & activate virtual environment (optional)
python -m venv venv
source venv/bin/activate   # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations to current head
alembic upgrade head

# Start FastAPI development server
uvicorn app.main:app --reload --port 8000
```

#### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```

---

## 🔒 Role-Based Portals

| Role | Portal URL | Core Features |
|---|---|---|
| **Trainee** | `/trainee/dashboard` | Consent management, SkillPulse ID, longitudinal journey tracking, AI skill gap analysis, employment reporting, wage growth tracking, follow-up responses. |
| **Training Provider** | `/provider/dashboard` | Course creation, batch scheduling, trainee enrollment, CSV roster bulk ingestion, course-level placement metrics. |
| **Employer** | `/employer/dashboard` | Pending employment verification requests, payroll confirmation, candidate talent discovery with consenting graduate filtering. |
| **Admin / Government** | `/admin/dashboard` | National outcome overview, macro employment rate, 6-month retention rate, average wage growth, district-level breakdown, provider impact rankings. |

---

## 🧪 Automated Testing Suite

The application includes a comprehensive test suite in `backend/tests/` covering the full lifecycle:

```bash
cd backend
pytest tests/ -v
```

### Test Coverage Highlights:
- **Authentication & RBAC**: Tests registration across all roles, password hashing, JWT creation, and rejection of unauthorized cross-role endpoints.
- **SkillPulse ID & Consent**: Verifies non-sequential `SP-XXXXXXXX` format, cryptographic uniqueness, consent granting with purpose, revocation, and immutable audit logs.
- **Skills Normalization & Courses**: Tests canonical casing (e.g. `python` → `Python`), duplicate prevention, course creation, batch creation, and trainee enrollment.
- **Employment & Employer Verification**: Tests trainee self-reporting, calculation of confidence score based on verification criteria, and wage history updates.
- **Longitudinal Follow-Ups**: Tests 30-day, 90-day, 6-month, and 12-month schedule generation and response recording.
- **Zero-Data & Populated Analytics**: Validates all 8 `/analytics` endpoints with zero initial records (ensuring clean responses without exceptions) and verifies SQL aggregations when data is populated.
- **AI Service Resilience**: Tests safe error handling and output structure when `AI_API_KEY` is not configured.

---

## 📄 License

SkillPulse is released under the MIT License.

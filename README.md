# CampusSkill AI — College Placement & Skill Gap Analyzer

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11%2B-blue?style=for-the-badge&logo=python" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/Flask-3.1-black?style=for-the-badge&logo=flask" alt="Flask 3.1">
  <img src="https://img.shields.io/badge/SQLAlchemy-ORM-red?style=for-the-badge" alt="SQLAlchemy">
  <img src="https://img.shields.io/badge/Bootstrap-5.3-purple?style=for-the-badge&logo=bootstrap" alt="Bootstrap 5.3">
  <img src="https://img.shields.io/badge/Chart.js-4.4-orange?style=for-the-badge" alt="Chart.js">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
</p>

**CampusSkill AI** is a production-grade, full-stack web application designed for engineering colleges, training & placement cells, and university students. The platform analyzes student competencies against real-world job role requirements, calculates explainable placement readiness scores, pinpoints critical skill gaps, and generates structured 4-phase learning roadmaps.

---

## 1. Problem Statement & Academic Solution

### The Challenge
- **Curriculum vs Industry Divide**: Engineering students often graduate without clear visibility into which specific technical skills and proficiency levels hiring companies demand.
- **Vague Preparation**: Students study without structured milestones or actionable roadmaps, often focusing on redundant topics while neglecting critical hiring filters like SQL window functions, System Design, or Aptitude.
- **Lack of Institutional Visibility**: College Training & Placement (T&P) cells lack centralized, real-time analytics to detect common batch deficits and schedule timely skill-building bootcamps before recruitment drives commence.

### The Solution: CampusSkill AI
1. **Explainable Placement Readiness Calculator**: Computes a transparent composite score based on Technical Role Alignment (40%), Aptitude (20%), DSA (20%), Communication (10%), and Verified practice assessments (10%).
2. **Deterministic Skill Gap Analysis Engine**: Directly compares student proficiencies (Beginner, Intermediate, Advanced) with industry job benchmarks to categorize competencies into *Missing*, *Needs Improvement*, and *Proficient*.
3. **Automated 4-Phase Personalized Roadmaps**: Converts identified gaps into an actionable pathway:
   - **Phase 1**: Core Fundamentals
   - **Phase 2**: Practical Hands-on Exercises
   - **Phase 3**: Mini-Portfolio Projects
   - **Phase 4**: Placement Interview & STAR Behavioral Preparation
4. **T&P Cell Cohort Analytics**: Real-time distribution charts by branch and year, aggregated skill deficit rankings, and single-click CSV export of placement records.
5. **Timed Practice Assessments**: Working question banks with instant score calculation, question-by-question explanations, and empirical verification badges.

---

## 2. Key User Roles & Permissions (RBAC)

The platform implements strict backend Role-Based Access Control:

| Role | Access Privileges |
|---|---|
| **Student** | Self-registration, profile management, skills portfolio CRUD, target job goal setting, skill gap analyzer, personalized roadmaps (with database-persisted completion check-offs), timed assessments, and resume upload. |
| **Placement Officer** | Cohort analytics dashboard, branch and year breakdowns, batch readiness tier distribution, top missing skills across all students, student search/filter, individual gap reports, and CSV report exports. |
| **Administrator** | User account management (activation/deactivation, role promotion), job-role catalog management, skill requirements and weight adjustments, assessment question authoring, and audit logging. |

---

## 3. Technology Stack

- **Backend**: Python 3.11+, Flask (Application Factory pattern), Flask-Login (session authentication), Werkzeug (password hashing).
- **Database & ORM**: SQLite (development default) / PostgreSQL compatible via Flask-SQLAlchemy 3.1 & SQLAlchemy 2.0.
- **Frontend & UI**: HTML5, CSS3, JavaScript (Vanilla ES6+), Bootstrap 5.3, Bootstrap Icons, Chart.js 4.4.
- **Security**: Cryptographic CSRF protection tokens, safe file upload sanitization with randomized filenames, HTTP-only secure cookies, and `@role_required` decorators.
- **Testing**: Pytest with automated unit and integration tests.

---

## 4. Quick Start & Local Setup

### Step 1: Clone or Open the Repository
```bash
git clone https://github.com/Kartikbodhe/CampusSkill-AI.git
cd CampusSkill-AI
```

### Step 2: Set Up Virtual Environment & Dependencies
```powershell
# Create virtual environment
python -m venv venv

# Activate on Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Or on Linux/macOS:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables
Copy `.env.example` to `.env`:
```powershell
copy .env.example .env
```
Default `.env` settings:
```env
FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=campusskill-dev-secret-key-389f41bce8a149f
DATABASE_URL=sqlite:///campusskill.db
MAX_CONTENT_LENGTH=5242880
UPLOAD_FOLDER=uploads
```

### Step 4: Run the Application
```powershell
python app.py
```
Open [http://localhost:5000](http://localhost:5000) in your web browser.

---

## 5. Pre-seeded Demo Accounts

The database seeds automatically on first launch with comprehensive sample data and accounts:

| Role | Email | Password | Pre-loaded Context |
|---|---|---|---|
| **Student** | `student@campusskill.edu` | `Student@123` | Rahul Sharma (CS 3rd Year) with pre-entered skills and target goal set to Data Analyst. |
| **Placement Officer** | `placement@campusskill.edu` | `Placement@123` | Full access to batch analytics, branch distributions, and CSV export. |
| **Administrator** | `admin@campusskill.edu` | `Admin@123` | System admin console with user status toggle and audit log views. |

---

## 6. Running Automated Tests

Run the test suite with `pytest`:
```powershell
.\venv\Scripts\pytest tests/
```
Expected output:
```text
tests/test_auth.py ....                [ 26%]
tests/test_permissions.py ....         [ 53%]
tests/test_phase1.py ...               [ 73%]
tests/test_readiness.py ..             [ 86%]
tests/test_skill_gap.py ..             [100%]
===================== 15 passed in ~12s =====================
```

---

## 7. Project Directory Structure

```text
CampusSkill-AI/
├── app.py                     # Flask application factory (create_app)
├── config.py                  # Environment-based configuration classes
├── extensions.py              # Centralized SQLAlchemy & LoginManager instances
├── requirements.txt           # Python package specifications
├── .env.example               # Configuration template
├── .gitignore                 # Excludes venv, database, cache, and uploads
├── README.md                  # Comprehensive documentation
├── models/                    # Relational database models
│   ├── __init__.py            # Model exports
│   ├── user.py                # User & StudentProfile models
│   ├── skills.py              # Skill & StudentSkill models
│   ├── jobs.py                # JobRole & JobRoleSkill models
│   ├── assessments.py         # Assessment, Question, Attempt & Answer models
│   ├── roadmap.py             # Roadmap & RoadmapTask models
│   └── audit.py               # AuditLog security model
├── routes/                    # Modular Flask blueprints
│   ├── __init__.py            # Blueprint registry
│   ├── main.py                # Public landing page & /health endpoint
│   ├── auth.py                # Registration, login, logout & role redirection
│   ├── student.py             # Student dashboard, profile & resume upload
│   ├── skills.py              # Skills portfolio CRUD
│   ├── analyzer.py            # Skill Gap Analyzer & Job Explorer
│   ├── roadmap.py             # Learning roadmap & task persistence
│   ├── assessments.py         # Practice tests & answer explanations
│   ├── placement.py           # Placement officer analytics & CSV export
│   └── admin.py               # Admin console, user status & question authoring
├── services/                  # Deterministic intelligence & analytics services
│   ├── __init__.py
│   ├── skill_gap.py           # Weighted skill gap analysis calculation
│   ├── readiness.py           # Composite placement readiness calculator
│   ├── roadmap_generator.py   # 4-phase structured roadmap generator
│   ├── role_matcher.py        # Best-fit job role recommendation
│   └── seed_data.py           # Database initial seeder
├── static/
│   ├── css/
│   │   └── style.css          # SaaS dark-theme stylesheet
│   └── js/
│       └── main.js            # Interactive client handlers & timer
├── templates/
│   ├── base.html              # Master layout with responsive navbar & alerts
│   ├── index.html             # Public SaaS landing page
│   ├── auth/                  # Login & registration views
│   ├── student/               # Student dashboard, profile, skills, analyzer, roadmap
│   ├── assessments/           # Test catalog, timed exam, and review views
│   ├── placement/             # Placement officer dashboard & student reports
│   ├── admin/                 # Administrator console & audit trail
│   └── errors/                # Custom error templates (400, 403, 404, 500)
├── tests/                     # Pytest automated test suites
└── uploads/                   # Secure storage for uploaded student resumes
```

---

## 8. Deployment to Production (e.g., Render)

CampusSkill AI is configured for production deployment on platforms like [Render](https://render.com) or any cloud VPS.

### Build and Start Commands
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app`

### Environment Variables
Configure these in your Render or cloud dashboard:
```env
FLASK_ENV=production
SECRET_KEY=<generate-a-strong-random-key>
DATABASE_URL=<your-postgresql-connection-string>
MAX_CONTENT_LENGTH=5242880
UPLOAD_FOLDER=uploads
```

*Note: If `DATABASE_URL` uses the legacy `postgres://` prefix, `config.py` automatically adapts it to `postgresql://` for SQLAlchemy 2.0 compatibility.*

---

## 9. Academic Transparency & Disclaimers

- **Educational Metric**: Placement readiness scores and roadmap tasks are deterministic algorithmic guidance metrics calculated from student inputs and practice evaluations. They serve as structured preparation pathways and do not guarantee corporate hiring.
- **Sample Requirements**: Job role skill requirements are structured reference benchmarks curated from industry standards, not official guarantees of specific employer criteria.

---

## 10. License

This project is licensed under the MIT License — see the LICENSE file for details.

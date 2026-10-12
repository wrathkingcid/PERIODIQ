# PERIODIQ — Universal Automatic Timetable Generator and Scheduler

> **State-of-the-art AI-assisted academic scheduling & timetable optimization engine** powered by **Google OR-Tools CP-SAT**, built for Schools, Colleges, Universities, and Coaching Institutes.

---

## 🌟 Highlights & Architecture

- **Constraint Optimization Engine**: Google OR-Tools CP-SAT (`ortools.sat.python.cp_model`) modeling hard and soft constraints with multi-threaded branch-and-bound search.
- **Infeasibility Explainer**: When a curriculum or workload combination cannot mathematically fit, PERIODIQ pinpoints the exact root causes (e.g. Teacher Over-allocation, Room Bottleneck, Lab Deficit) and suggests actionable remedies rather than publishing invalid schedules.
- **Intelligent Shift Planning**: Analyzes room concurrency, laboratory throughput, student counts, and faculty capacity to recommend **Single Shift** vs. **Morning/Afternoon Dual Shifts**, evaluating operating costs and room ROI without hiding true resource deficits.
- **Document & File Ingestion Wizard**: Automatically parses `.xlsx`, `.csv`, `.pdf` documents, detects subjects, weekly hours, practical blocks, teachers, and rooms, flags contradictions, and presents essential clarification questions.
- **Interactive Timetable Studio**:
  - Filter by **Class/Division**, **Faculty**, or **Room/Laboratory**.
  - Drag-and-drop & manual slot moves with **real-time conflict detection** (flags teacher clashes, room clashes, or division clashes).
  - Pinning / Locking periods: Locked periods remain intact during re-runs.
  - Multi-period practical lab blocks (e.g. 2-period lab).
  - One-click **Styled Excel Export (.xlsx)** and **Print-Ready Timetable**.
- **Three Realistic Institutional Profiles Pre-loaded**:
  1. **Greenwood International High School** (K-12 STEM labs, 7 periods/day, 5 days/wk)
  2. **Apex Institute of Technology** (Engineering university, credit framework, theory + 2-period lab blocks, 6 days/wk)
  3. **Olympus IIT-JEE & NEET Academy** (Intensive coaching, 60-min periods, morning & evening cohorts)

---

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 19, TypeScript, Tailwind CSS, Lucide Icons |
| **Backend API** | Python 3.12, FastAPI, Pydantic v2, Uvicorn |
| **Database & ORM** | PostgreSQL (with seamless SQLite zero-config fallback), SQLAlchemy 2.0 |
| **Optimization Engine** | Google OR-Tools CP-SAT (Constraint Programming) |
| **Document Processing** | OpenPyXL, PyPDF, Regex tabular extractors |

---

## 🚀 Quickstart & Local Setup

### 1. Prerequisites
- **Python 3.10+** (Python 3.12 tested and verified)
- **Node.js 18+** & npm

### 2. Backend Setup
```bash
cd backend

# Install dependencies
python -m pip install fastapi uvicorn ortools sqlalchemy pydantic pydantic-settings PyJWT openpyxl pypdf pytest

# (Optional) Set DATABASE_URL in .env if using PostgreSQL:
# DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/periodiq

# Run automated tests for CP-SAT constraints and shift planner:
python -m pytest tests/test_solver.py -v
python -m pytest tests/test_infeasibility.py -v

# Start FastAPI server:
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
API documentation is available at: `http://127.0.0.1:8000/docs`

### 3. Frontend Setup
```bash
cd frontend

# Install npm dependencies
npm install

# Build for production
npm run build

# Start Vite dev server:
npm run dev -- --host 127.0.0.1 --port 5173
```
Open `http://127.0.0.1:5173` in your browser.

---

## 📐 Mathematical Formulation & CP-SAT Constraints

### Hard Constraints (Enforced 100%)
1. **Division Non-Overlap**: $\sum_{i \in Sessions(c)} active_{i, d, p} \le 1$ for all divisions $c$, days $d$, slots $p$.
2. **Teacher Non-Overlap**: $\sum_{i} assign\_teacher_{i, t, d, p} \le 1$ for all teachers $t$, days $d$, slots $p$.
3. **Room Non-Overlap**: $\sum_{i} assign\_room_{i, r, d, p} \le 1$ for all rooms $r$, days $d$, slots $p$.
4. **Subject Required Hours**: Exactly $\frac{WeeklyHours_{c,u}}{BlockLength}$ sessions scheduled.
5. **Consecutive Block Scheduling**: Lab practicals occupy continuous periods $p, p+1$ without interruption.
6. **Teacher Competency Matching**: Faculty only assigned to subjects in their competency profile.
7. **Room Suitability**: Labs assigned to corresponding specialized room types; classroom capacity $\ge$ division student count.
8. **Teacher Blackout Slots**: Zero assignments permitted during unavailable hours.
9. **Teacher Daily & Weekly Limits**: Total teaching hours $\le$ maximum daily and weekly workload.
10. **Locked / Pinned Assignments**: Pinned entries are locked as fixed constants during re-solving.

### Soft Constraints & Quality Objectives
- **Subject Spread Penalty**: Penalizes scheduling the same lecture subject multiple times in a single day.
- **Teacher Idle Gap Penalty**: Penalizes scattered single-period gaps between classes on the same day.
- **Faculty Preferred Window Reward**: Rewards assigning faculty to their requested time slots.

---

## 📂 Project Directory Structure

```
PERIODIQ/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI app entry point & routes
│   │   ├── database.py              # SQLAlchemy engine & session factory
│   │   ├── core/                    # Config & JWT security
│   │   ├── models/                  # Institution, User, Academic, Timetable, Audit models
│   │   ├── schemas/                 # Pydantic request/response schemas
│   │   ├── solver/
│   │   │   ├── cp_sat_engine.py     # Google OR-Tools CP-SAT scheduler
│   │   │   └── infeasibility_explainer.py # Bottleneck diagnostics
│   │   ├── services/
│   │   │   ├── shift_planner.py     # Single vs multi-shift capacity evaluator
│   │   │   ├── document_parser.py   # PDF, Excel, CSV extractor
│   │   │   ├── sample_data_loader.py# High School, College, Coaching seeds
│   │   │   └── export_service.py    # Formatted .xlsx generator
│   │   └── api/v1/                  # REST endpoints
│   └── tests/                       # Automated Pytest suite
├── frontend/
│   ├── src/
│   │   ├── App.tsx                  # Main application orchestrator
│   │   ├── components/
│   │   │   ├── Navbar.tsx           # Institutional switcher & action bar
│   │   │   ├── TimetableGrid.tsx    # Interactive timetable calendar
│   │   │   ├── ShiftPlannerStudio.tsx # Shift planning & capacity visualizer
│   │   │   ├── IngestionWizard.tsx  # Document upload, extraction & review
│   │   │   ├── ResourcesView.tsx    # Catalog of faculty, rooms, curriculum
│   │   │   ├── AnalyticsView.tsx    # Workload meters & scenario comparison
│   │   │   ├── GenerateModal.tsx    # Solver parameter dialog
│   │   │   └── InfeasibilityModal.tsx # Diagnostic explainer modal
│   │   └── services/api.ts          # Frontend API client
└── README.md
```

---

## 📄 License
MIT License. Built for modern educational institution timetable administration.

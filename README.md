# 🎓 College Management System

A full-stack college management application built with **Flask** (backend) and **plain HTML/CSS/JS** (frontend), featuring a dual dark/light theme, JWT authentication, comprehensive report generation, and an AI assistant (AIRA).

---

## 📦 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11+, Flask 3.x, PyMySQL |
| Database | MySQL (XAMPP) |
| Auth | JWT (PyJWT + bcrypt) |
| Frontend | HTML5, CSS3, Vanilla JS |
| AI | Ollama (local, `gemma3:1b` recommended) / Google Gemini |

---

## 🚀 Quick Start

### Prerequisites
- [XAMPP](https://www.apachefriends.org/) with **MySQL** running on port `3306`
- [Python 3.11+](https://www.python.org/)
- [uv](https://docs.astral.sh/uv/) — fast Python package manager (`pip install uv`)
- [Ollama](https://ollama.ai/) (optional but recommended for AIRA)

---

### 1. Database Setup

1. Start **MySQL** in XAMPP Control Panel.
2. Import the schema and seed data using the full path to XAMPP's MySQL:

```powershell
# From the project root — use the full path to xampp's mysql.exe
& "C:\xampp\mysql\bin\mysql.exe" -u root college_management < Main/Backend/database/schema.sql
& "C:\xampp\mysql\bin\mysql.exe" -u root college_management < Main/Backend/database/seed.sql
```

> If the `college_management` database doesn't exist yet, create it first in phpMyAdmin or run:
> ```powershell
> & "C:\xampp\mysql\bin\mysql.exe" -u root -e "CREATE DATABASE college_management CHARACTER SET utf8mb4;"
> ```

#### Applying the Report Migration (if upgrading)

If you already have the base schema and need to add the report-generation tables:

```powershell
Get-Content "Main/Backend/database/migration_reports.sql" | & "C:\xampp\mysql\bin\mysql.exe" -u root
```

---

### 2. Backend Setup

```powershell
cd Main/Backend

# Create and activate a virtual environment with uv
uv venv
.venv\Scripts\activate

# Install all dependencies
uv pip install -r requirements.txt

# Copy and configure .env
copy .env.example .env
```

Edit `Main/Backend/.env`:
```env
FLASK_SECRET_KEY=your-super-secret-key-here
FLASK_DEBUG=True

DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=          # Leave blank for default XAMPP (no password)
DB_NAME=college_management

JWT_SECRET_KEY=your-jwt-secret-key
JWT_EXPIRY_HOURS=24

# Important: add the frontend origin here to avoid CORS issues
CORS_ORIGINS=http://localhost:8000,http://localhost,http://127.0.0.1
```

Start the backend server:
```powershell
# With uv (recommended — no manual venv activation needed)
uv run python run.py
```

The API will be available at `http://localhost:5000/api`

---

### 3. Frontend (Serve via Python HTTP server)

```powershell
cd Main/Frontend
uv run python -m http.server 8000
# OR if Python is on PATH:
python -m http.server 8000
```

Navigate to: **`http://localhost:8000/login.html`**

---

### Default Login Credentials

| Username | Password | Role |
|----------|----------|------|
| `superadmin` | `Admin@123` | Super Admin |

> ⚠️ **Change the default password immediately after first login!**

---

### 4. (Optional) Populate Complete Database

The project includes a powerful script to simulate a fully-functioning engineering college. Note: **Running this will DELETE all existing data in your database** and generate fresh data.

It generates:
- 4 Academic Years & 6 Departments
- 12 Courses & ~480 Subjects
- 1500 Students & 150 Staff
- Attendance, Marks, Fees, Timetables, Scholarships, and more!

Ensure XAMPP MySQL is running, then run:

```powershell
# Must run from Main/Backend so uv uses the correct .venv
cd Main\Backend
uv run python ..\..\populate_db.py
```

> **Why not from the project root?** The `.venv` with all dependencies lives inside `Main/Backend/`. Running `uv run` from the project root creates a fresh empty environment and fails with `ModuleNotFoundError: No module named 'pymysql'`.

---

## 🤖 AIRA — AI Research Assistant

AIRA is a built-in AI assistant that answers natural-language questions about students, staff, attendance, marks, fees, and generates comprehensive reports using live database data.

### Built-in Mode (No LLM Required)
AIRA works immediately **without any LLM** for common queries and reports:

| Category | Example Queries |
|----------|----------------|
| **Student Data** | "How many students?", "List students", "Student profile report" |
| **CGPA / Profile** | "Show student CGPA report", "Profile report" |
| **Departments** | "Department summary", "How many departments?" |
| **Staff** | "How many staff?", "List staff" |
| **Attendance** | "Overall attendance", "Attendance report" |
| **Marks** | "Marks report", "Show marks" |
| **Fees** | "Total fees collected?", "Fee structure report" |
| **Eligibility** | "Eligibility report", "Eligible students" |
| **Categories** | "Category wise report", "Centac students" |
| **Scholarships** | "Scholarship report", "Caste wise scholarships" |
| **Activities** | "Extracurricular activities", "Technical activities" |

Type **"help"** to see all supported built-in commands.

### Full AI Mode — Ollama (Free & Local, Recommended)

```powershell
# Install Ollama from https://ollama.ai, then pull a model:
ollama pull gemma3:1b
# Ollama runs automatically on http://localhost:11434
```

> **Important:** The default configured model is `gemma3:1b`. If you pull a different model (e.g., `mistral`, `llama3.2`), update it in **Settings → LLM Config** inside the app.

### Full AI Mode — Google Gemini

1. Get an API key from [Google AI Studio](https://aistudio.google.com/)
2. Go to **Settings → AIRA / LLM Config** in the app
3. Select **Gemini** as provider, enter your API key and model (e.g., `gemini-1.5-flash`)

---

## 🗂️ Project Structure

```
management-system/
├── Main/
│   ├── Backend/
│   │   ├── app/
│   │   │   ├── __init__.py              # Flask app factory — CORS, blueprint registration, strict_slashes=False
│   │   │   ├── db.py                    # PyMySQL connection pool — query() and execute() helpers
│   │   │   ├── utils/
│   │   │   │   ├── auth.py              # bcrypt password hashing, JWT token creation/verification, login_required decorator
│   │   │   │   └── response.py          # Standard JSON responses — success/error helpers, timedelta/Decimal serializer
│   │   │   └── routes/                  # 12 module blueprints (one file per module)
│   │   │       ├── auth.py              # POST /login, /change-password — JWT authentication flow
│   │   │       ├── college.py           # College info CRUD, departments list, academic years
│   │   │       ├── courses.py           # Courses CRUD, subjects CRUD (accepts both 'semester' and 'semester_number')
│   │   │       ├── students.py          # Student CRUD — includes student_category, caste_community fields
│   │   │       ├── staff.py             # Staff CRUD, subject allocations
│   │   │       ├── timetable.py         # Timetable CRUD, period definitions, rooms
│   │   │       ├── marks.py             # Exams CRUD, bulk mark entry, semester results with GPA/CGPA
│   │   │       ├── attendance.py        # Bulk attendance entry, attendance summary
│   │   │       ├── fees.py              # Fee structures, payments, scholarships
│   │   │       ├── reports.py           # 12 report endpoints — see Reports section below
│   │   │       ├── aira.py              # AIRA: 14 MCP tools, smart fallback, Ollama/Gemini bridge, DB context injection
│   │   │       └── notifications.py     # Parent notification templates, send via email/SMS/WhatsApp
│   │   ├── database/
│   │   │   ├── schema.sql               # 38-table schema — full database definition
│   │   │   ├── seed.sql                 # Initial roles, college, academic year, superadmin (bcrypt hash)
│   │   │   └── migration_reports.sql    # Migration: student_category/caste_community columns + 3 new tables
│   │   ├── config.py                    # Environment variable loading (.env)
│   │   ├── run.py                       # Flask development server entry point (port 5000)
│   │   ├── requirements.txt             # Python dependencies: Flask, PyMySQL, PyJWT, bcrypt, requests, google-genai
│   │   └── .env.example                 # Template for environment configuration
│   └── Frontend/
│       ├── assets/
│       │   ├── css/
│       │   │   ├── main.css             # Complete design system — dual theme (light/dark), stat-cards, tables, forms, badges
│       │   │   └── aira.css             # AIRA widget styles — floating bubble, chat window, quick actions, animations
│       │   └── js/
│       │       ├── api.js               # Fetch API client — auto-injects JWT token, handles 401 redirects
│       │       ├── auth.js              # JWT auth management — requireAuth(), getUser(), logout()
│       │       ├── theme.js             # Dark/light theme toggle — saves preference to localStorage
│       │       ├── utils.js             # Shared utilities — toast(), formatDate(), formatCurrency(), renderTable(), statusBadge(), attendanceColor()
│       │       ├── sidebar.js           # Shared sidebar renderer — nav links with active state, role-based filtering
│       │       └── aira.js              # AIRA chat widget — 7 quick actions, markdown rendering, chat history
│       ├── login.html                   # Login page — username/password form, JWT token storage
│       ├── dashboard.html               # Dashboard — stat cards, department overview, quick actions
│       ├── students/
│       │   ├── index.html               # Student list — search, filter, add/edit modal
│       │   └── add.html                 # Add/edit student form — includes student_category, caste_community
│       ├── staff/
│       │   ├── index.html               # Staff list — filterable, add/edit modal
│       │   └── add.html                 # Add/edit staff form
│       ├── departments/
│       │   └── index.html               # Department management — add, edit, assign HOD
│       ├── courses/
│       │   └── index.html               # Courses & subjects — CRUD with semester assignment
│       ├── timetable/
│       │   └── index.html               # Visual weekly timetable grid — drag-and-drop scheduling
│       ├── attendance/
│       │   └── index.html               # Bulk attendance entry — section-based, date picker
│       ├── marks/
│       │   └── index.html               # Bulk mark entry — exam management, semester results
│       ├── fees/
│       │   └── index.html               # Fee structures, payments, scholarships management
│       ├── reports/
│       │   └── index.html               # 12 report cards with dynamic filters, CSV export
│       ├── notifications/
│       │   └── index.html               # Parent notification templates, send history
│       └── settings/
│           └── index.html               # LLM config (Ollama/Gemini), system settings
├── er_diagrams.html                     # Interactive ER diagrams (9 sections) rendered with Mermaid.js
├── college_management_requirements.md   # Full requirements document — 38 entities, 12 modules, ER diagrams
├── populate_db.py                       # Script to seed realistic sample data via API calls
├── test_aira.py                         # AIRA chatbot automated tests
└── README.md                           # This file
```

---

## 📊 Reports Module

The Reports module provides **12 report types** accessible through both the **Reports page UI** and the **AIRA chatbot**:

### Original Reports
| # | Report | Endpoint | Description |
|---|--------|----------|-------------|
| 1 | Attendance Defaulters | `GET /api/reports/attendance` | Students below attendance threshold |
| 2 | Marks Summary | `GET /api/reports/marks` | GPA/CGPA semester results |
| 3 | Fee Defaulters | `GET /api/reports/fee-defaulters` | Students with pending fee balance |
| 4 | Department Summary | `GET /api/reports/department-summary` | Department-wise student/staff/course counts |

### New Reports (Added)
| # | Report | Endpoint | Description |
|---|--------|----------|-------------|
| 5 | Student Profile / CGPA | `GET /api/reports/student-profile` | Name, reg no, CGPA, course, category |
| 6 | Fee Structure | `GET /api/reports/fee-structure` | Breakdown by course, category, semester |
| 7 | Eligibility Criteria | `GET /api/reports/eligibility` | Match/unmatch per student against criteria |
| 8 | Category-wise | `GET /api/reports/category-wise` | Centac/management/regular breakdown |
| 9 | Scholarship | `GET /api/reports/scholarship` | Caste/community-wise scholarship data |
| 10 | Extracurricular | `GET /api/reports/extracurricular` | Technical & non-technical activities |
| 11 | Attendance Detailed | `GET /api/reports/attendance-detailed` | Flexible filters: class, student, dept, subject, date range |
| 12 | Marks Detailed | `GET /api/reports/marks-detailed` | Flexible filters: class, student, dept, subject, exam type |

All reports support **query parameter filters** and can be **exported to CSV** from the UI.

---

## 🔐 Roles & Access

| Role | Access |
|------|--------|
| `super_admin` | Full system access |
| `admin` | College administration |
| `hod` | Department-level access |
| `staff` | Teaching staff features |

---

## 📊 Modules

| # | Module | Features |
|---|--------|---------|
| 1 | Auth | Login, JWT, password change |
| 2 | College | College info, departments, academic years |
| 3 | Courses | Courses, subjects, semesters |
| 4 | Students | Batches, sections, student CRUD (with category & caste/community) |
| 5 | Staff | Staff CRUD, subject allocations |
| 6 | Timetable | Visual weekly timetable grid |
| 7 | Marks | Exams, bulk mark entry, results, GPA/CGPA |
| 8 | Attendance | Bulk attendance, summary, % tracking |
| 9 | Fees | Fee structures, payments, scholarships |
| 10 | Reports | 12 report types + CSV export (see Reports section) |
| 11 | AIRA | AI assistant — 14 MCP tools, smart fallback, Ollama/Gemini |
| 12 | Notifications | Parent notifications via email/SMS/WhatsApp |

---

## 🗄️ Database Schema (38 Tables)

| # | Table | Purpose |
|---|-------|---------|
| 1 | `college` | College info (multi-campus ready) |
| 2 | `academic_year` | Year labels, start/end dates |
| 3 | `department` | Departments with HOD assignment |
| 4 | `course` | Courses with degree type |
| 5 | `semester` | Semester periods per academic year |
| 6 | `subject` | Subjects with credits and type |
| 7 | `batch` | Admission year grouping |
| 8 | `section` | Class divisions (A, B, C) |
| 9 | `staff` | Faculty master data |
| 10 | `student` | Student master + `student_category`, `caste_community` |
| 11 | `role` | Access roles (super_admin, admin, hod, staff) |
| 12 | `user_account` | Login credentials |
| 13 | `activity_log` | Audit trail |
| 14 | `subject_allocation` | Staff ↔ Subject ↔ Section mapping |
| 15 | `room` | Classrooms & labs |
| 16 | `period_definition` | Time slots |
| 17 | `timetable` | Schedule entries |
| 18 | `exam_type` | Internal/External/Assignment/Lab |
| 19 | `exam` | Specific exam instances |
| 20 | `mark` | Student scores |
| 21 | `grade_mapping` | % → Grade → Grade Point |
| 22 | `semester_result` | GPA/CGPA per student |
| 23 | `attendance` | Period-wise attendance records |
| 24 | `fee_category` | Mgmt quota, govt, SC/ST, etc. |
| 25 | `fee_component` | Tuition, lab, library, etc. |
| 26 | `fee_structure` | Course + Category → Total |
| 27 | `fee_structure_detail` | Component-level breakdown |
| 28 | `fee_payment` | Transaction records |
| 29 | `scholarship` | Concession tracking |
| 30 | `aira_conversation` | Chat sessions per user |
| 31 | `aira_message` | Chat messages with tool calls/results |
| 32 | `aira_action_log` | AI-initiated action audit trail |
| 33 | `llm_config` | AI model configuration per college |
| 34 | `notification_template` | Saved message formats |
| 35 | `notification_log` | Sent notification history |
| 36 | `extracurricular_activity` | Student activities (technical & non-technical) |
| 37 | `eligibility_criteria` | Configurable eligibility rules with thresholds |
| 38 | `student_eligibility` | Student ↔ Criteria evaluation mapping |

---

## 🛠️ Known Fixes Applied

The following bugs were identified and resolved during initial setup:

| Issue | Root Cause | Fix Applied |
|-------|-----------|-------------|
| Invalid password on login | Default `seed.sql` used a PHP-style bcrypt hash incompatible with Python's `bcrypt` library | Regenerated hash using `bcrypt.hashpw()` in Python |
| CORS errors on Timetable/Attendance pages | Backend returned `500 Internal Server Error` for period definitions due to unserializable `datetime.timedelta` objects, causing CORS headers to drop | Added `_serialize()` helper in `app/utils/response.py` to convert `timedelta` and `Decimal` to JSON-safe types |
| `login_required` blocking OPTIONS preflight | The auth decorator did not short-circuit `OPTIONS` method requests | Added `OPTIONS` pass-through in decorator |
| AIRA using wrong Ollama model | Backend was hard-coded to `llama3.2` which may not be installed | Updated default to `gemma3:1b`; all references now use `gemma3:1b` |
| `add_subject` API 500 error | Frontend sent field as `semester`, backend expected `semester_number` | Route now accepts both field names |
| Blueprint trailing-slash issues | Flask strict_slashes default caused redirect on trailing-slash mismatch | Set `app.url_map.strict_slashes = False` in app factory |
| AIRA "show student" keyword collision | "Show student CGPA report" matched generic "show student" before CGPA report handler | Added `is_report_query` guard to check report-specific keywords first |

---

## 🎨 Theming

The app supports **dark and light themes** toggled via the 🌙/☀️ button in the header. Theme preference is saved in `localStorage`.

CSS custom properties are defined in `assets/css/main.css` under `:root` (light) and `[data-theme="dark"]`.

---

## 🤖 Agent / Automation Notes

> These notes are specifically for AI agents running this project. All three issues below caused failures in automated test runs.

### ⚠️ 1. Starting the Frontend Server on Windows

**Problem:** Running `python -m http.server 8000` as an inline background command in PowerShell can silently die due to keyboard-interrupt signals from the shell.

**Fix — always use `Start-Process` to launch it in a separate process:**

```powershell
Start-Process -FilePath "python" -ArgumentList "-m", "http.server", "8000" `
  -WorkingDirectory "C:\xampp\htdocs\management-system\Main\Frontend" `
  -WindowStyle Normal
```

This keeps the server alive independently. Verify it's up by opening `http://localhost:8000/login.html`.

---

### ⚠️ 2. `DB_PASSWORD` in `.env` — No Inline Comments

**Problem:** `python-dotenv` reads **everything after the `=`** as the value, including inline comments and trailing spaces:

```env
# ❌ WRONG — password will be "          # Leave blank..." (non-empty string)
DB_PASSWORD=          # Leave blank for default XAMPP (no root password)
```

This causes `pymysql` to send a non-empty password to MySQL, resulting in:
```
OperationalError: (1045, "Access denied for user 'root'@'localhost' (using password: YES)")
```
Which then drops CORS headers on the 500 response, making browsers report a misleading CORS error.

**Fix — blank value, nothing after the `=`:**

```env
# ✅ CORRECT
DB_PASSWORD=
```

---

### ⚠️ 3. Browser Navigation — Always Use the Full HTML Path

**Problem:** Navigating to `http://localhost:8000` shows a **directory listing**, not the app. Clicking through the listing is unreliable and causes 404s.

**Fix — always navigate directly to the login page:**

```
http://localhost:8000/login.html
```

For automated testing you can also bypass the login form entirely by injecting the JWT token via JavaScript console:

```javascript
fetch('http://localhost:5000/api/auth/login', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({username: 'superadmin', password: 'Admin@123'})
}).then(r => r.json()).then(d => {
  localStorage.setItem('auth_token', d.data.token);
  window.location.href = '/dashboard.html';
});
```

---

### ⚠️ 4. Running `populate_db.py` — Use the Backend Directory

**Problem:** `uv run python populate_db.py` from the project root fails with `ModuleNotFoundError: No module named 'pymysql'` because `uv` finds no `.venv` there and creates a fresh empty environment.

**The `.venv` lives inside `Main/Backend/` — always run from there:**

```powershell
# ✅ CORRECT
cd Main\Backend
uv run python ..\..\populate_db.py
```

```powershell
# ❌ WRONG — uv creates an empty env at project root
uv run python populate_db.py
```

---

## 📝 License

MIT License — Free to use and modify.

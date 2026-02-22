# 🎓 College Management System

A full-stack college management application built with **Flask** (backend) and **plain HTML/CSS/JS** (frontend), featuring a dual dark/light theme, JWT authentication, and an AI assistant (AIRA).

---

## 📦 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11+, Flask 3.x, PyMySQL |
| Database | MySQL (XAMPP) |
| Auth | JWT (PyJWT + bcrypt) |
| Frontend | HTML5, CSS3, Vanilla JS |
| AI | Ollama (local, `gemma3` recommended) / Google Gemini |

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

### 4. (Optional) Seed Sample Data

After setting up the database, you can populate it with realistic sample data (2 departments, 2 courses, 4 subjects, 2 staff, 5 students) by running:

```powershell
# From the project root — backend must be running first!
uv run python populate_db.py
```

---

## 🤖 AIRA — AI Research Assistant

AIRA is a built-in AI assistant that answers natural-language questions about students, staff, attendance, marks, and fees using live database data.

### Built-in Mode (No LLM Required)
AIRA works immediately **without any LLM** for common queries:
- *"How many students are there?"*
- *"List all departments"*
- *"What is the overall attendance?"*
- *"Total fees collected?"*
- Type **"help"** to see all supported built-in commands.

### Full AI Mode — Ollama (Free & Local, Recommended)

```powershell
# Install Ollama from https://ollama.ai, then pull a model:
ollama pull gemma3
# Ollama runs automatically on http://localhost:11434
```

> **Important:** The default configured model is `gemma3`. If you pull a different model (e.g., `llama3.2`, `mistral`), update it in **Settings → LLM Config** inside the app.

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
│   │   │   ├── __init__.py          # Flask app factory (CORS, blueprints)
│   │   │   ├── db.py                # PyMySQL connection pool
│   │   │   ├── utils/
│   │   │   │   ├── auth.py          # bcrypt password hashing, JWT helpers
│   │   │   │   └── response.py      # Standard JSON responses (with timedelta/Decimal serializer)
│   │   │   └── routes/              # 12 module blueprints
│   │   │       ├── auth.py
│   │   │       ├── college.py
│   │   │       ├── courses.py       # Courses + Subjects (POST accepts 'semester' or 'semester_number')
│   │   │       ├── students.py
│   │   │       ├── staff.py
│   │   │       ├── timetable.py
│   │   │       ├── marks.py
│   │   │       ├── attendance.py
│   │   │       ├── fees.py
│   │   │       ├── reports.py
│   │   │       ├── aira.py          # AIRA: smart fallback + Ollama/Gemini bridge
│   │   │       └── notifications.py
│   │   ├── database/
│   │   │   ├── schema.sql           # 35-table schema
│   │   │   └── seed.sql             # Initial roles, college, superadmin (bcrypt hash)
│   │   ├── config.py
│   │   ├── run.py
│   │   ├── requirements.txt
│   │   └── .env.example
│   └── Frontend/
│       ├── assets/
│       │   ├── css/
│       │   │   ├── main.css         # Design system (dual theme)
│       │   │   └── aira.css         # AIRA widget styles
│       │   └── js/
│       │       ├── api.js           # Fetch API client (with JWT token handling)
│       │       ├── auth.js          # JWT auth management
│       │       ├── theme.js         # Dark/light toggle
│       │       ├── utils.js         # Shared utilities
│       │       ├── sidebar.js       # Shared sidebar renderer
│       │       └── aira.js          # AIRA chat widget
│       ├── login.html
│       ├── dashboard.html
│       ├── students/
│       ├── staff/
│       ├── departments/
│       ├── courses/
│       ├── timetable/
│       ├── attendance/
│       ├── marks/
│       ├── fees/
│       ├── reports/
│       ├── notifications/
│       └── settings/
├── populate_db.py                   # Script to seed realistic sample data via API
└── README.md
```

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
| 4 | Students | Batches, sections, student CRUD |
| 5 | Staff | Staff CRUD, subject allocations |
| 6 | Timetable | Visual weekly timetable grid |
| 7 | Marks | Exams, bulk mark entry, results, GPA |
| 8 | Attendance | Bulk attendance, summary, % tracking |
| 9 | Fees | Fee structures, payments, scholarships |
| 10 | Reports | Attendance/marks/fee reports + CSV export |
| 11 | AIRA | AI assistant (built-in + Ollama/Gemini) |
| 12 | Notifications | Parent notifications via email/SMS/WhatsApp |

---

## 🛠️ Known Fixes Applied

The following bugs were identified and resolved during initial setup:

| Issue | Root Cause | Fix Applied |
|-------|-----------|-------------|
| Invalid password on login | Default `seed.sql` used a PHP-style bcrypt hash incompatible with Python's `bcrypt` library | Regenerated hash using `bcrypt.hashpw()` in Python |
| CORS errors on Timetable/Attendance pages | Backend returned `500 Internal Server Error` for period definitions due to unserializable `datetime.timedelta` objects, causing CORS headers to drop | Added `_serialize()` helper in `app/utils/response.py` to convert `timedelta` and `Decimal` to JSON-safe types |
| `login_required` blocking OPTIONS preflight | The auth decorator did not short-circuit `OPTIONS` method requests | Added `OPTIONS` pass-through in decorator |
| AIRA using wrong Ollama model | Backend was hard-coded to `llama3.2` which may not be installed | Updated default to `gemma3`; configurable via Settings → LLM Config |
| `add_subject` API 500 error | Frontend sent field as `semester`, backend expected `semester_number` | Route now accepts both field names |
| Blueprint trailing-slash issues | Flask strict_slashes default caused redirect on trailing-slash mismatch | Set `app.url_map.strict_slashes = False` in app factory |

---

## 🎨 Theming

The app supports **dark and light themes** toggled via the 🌙/☀️ button in the header. Theme preference is saved in `localStorage`.

CSS custom properties are defined in `assets/css/main.css` under `:root` (light) and `[data-theme="dark"]`.

---

## 📝 License

MIT License — Free to use and modify.

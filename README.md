# 🎓 College Management System

A full-stack college management application built with **Flask** (backend) and **plain HTML/CSS/JS** (frontend), featuring a dual dark/light theme, JWT authentication, and an AI assistant (AIRA).

---

## 📦 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11+, Flask, PyMySQL |
| Database | MySQL (XAMPP) |
| Auth | JWT (PyJWT + bcrypt) |
| Frontend | HTML5, CSS3, Vanilla JS |
| AI | Ollama (local) / Google Gemini |

---

## 🚀 Quick Start

### Prerequisites
- [XAMPP](https://www.apachefriends.org/) with MySQL running
- [Python 3.11+](https://www.python.org/)
- [uv](https://docs.astral.sh/uv/) — fast Python package manager
- [Ollama](https://ollama.ai/) (optional, for AIRA AI assistant)

---

### 1. Database Setup

1. Start your local MySQL server (e.g., via **XAMPP**) and ensure it is running on port `3306`.
2. Import the database schema and seed data. From the root of the project, run:
   ```powershell
   mysql -u root < Main/Backend/database/schema.sql
   mysql -u root < Main/Backend/database/seed.sql
   ```
   *(If your MySQL root user has a password, add `-p` to the commands).*

---

### 2. Backend Setup

```powershell
# Navigate to backend directory from the project root
cd Main/Backend

# Create virtual environment using uv
uv venv

# Activate virtual environment (Windows)
.venv\Scripts\activate
# (On macOS/Linux use: source .venv/bin/activate)

# Install dependencies using uv
uv pip install -r requirements.txt

# Copy and configure environment
copy .env.example .env
# (On macOS/Linux use: cp .env.example .env)
```

Edit `.env` with your settings:
```env
FLASK_SECRET_KEY=your-super-secret-key-here
FLASK_DEBUG=True

DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=          # Leave blank for default XAMPP
DB_NAME=college_management

JWT_SECRET_KEY=your-jwt-secret-key
JWT_EXPIRY_HOURS=24

CORS_ORIGINS=http://localhost,http://127.0.0.1
```

Start the backend:
```powershell
python run.py
```

The API will be available at `http://localhost:5000/api`

---

### 3. Frontend Access

The frontend uses plain HTML/JS and can be served via any local web server.

**Option A: Using Python HTTP Server (Recommended for AI Agents / Any PC)**
```powershell
# From the project root, navigate to Frontend
cd Main/Frontend
# Start a simple HTTP server on port 8000
python -m http.server 8000
```
Navigate to: `http://localhost:8000/login.html`
*(Note: Ensure `CORS_ORIGINS` in your backend `.env` includes `http://localhost:8000`)*

**Option B: Using XAMPP Apache**
Place the project within the `htdocs` folder. Ensure Apache is running in XAMPP.
Navigate to: `http://localhost/management-system/Main/Frontend/login.html` *(adjust the URL path based on your folder name)*.

**Default Login Credentials:**
Use these credentials to log in to the system.
| Username | Password | Role |
|----------|----------|------|
| `superadmin` | `Admin@123` | Super Admin |

> ⚠️ **Change the default password immediately after first login!**

---

## 🗂️ Project Structure

```
management-system/
├── Main/
│   ├── Backend/
│   │   ├── app/
│   │   │   ├── __init__.py          # Flask app factory
│   │   │   ├── db.py                # PyMySQL connection
│   │   │   ├── utils/
│   │   │   │   ├── auth.py          # JWT helpers
│   │   │   │   └── response.py      # Standard JSON responses
│   │   │   └── routes/              # 12 module blueprints
│   │   │       ├── auth.py
│   │   │       ├── college.py
│   │   │       ├── courses.py
│   │   │       ├── students.py
│   │   │       ├── staff.py
│   │   │       ├── timetable.py
│   │   │       ├── marks.py
│   │   │       ├── attendance.py
│   │   │       ├── fees.py
│   │   │       ├── reports.py
│   │   │       ├── aira.py          # AIRA MCP bridge
│   │   │       └── notifications.py
│   │   ├── database/
│   │   │   ├── schema.sql           # 35-table schema
│   │   │   └── seed.sql             # Initial data
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
│       │       ├── api.js           # Fetch API client
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
└── README.md
```

---

## 🤖 AIRA — AI Research Assistant

AIRA is a built-in AI assistant that can query student data, attendance, marks, fees, and more using natural language.

### Setup with Ollama (Recommended — Free & Local)

```powershell
# Install Ollama from https://ollama.ai
# Pull a model
ollama pull llama3.2

# Ollama runs automatically on http://localhost:11434
```

### Setup with Google Gemini

1. Get an API key from [Google AI Studio](https://aistudio.google.com/)
2. Go to **Settings → AIRA / LLM Config** in the app
3. Select **Gemini** as provider, enter your API key and model name (e.g., `gemini-1.5-flash`)

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
| 2 | College | College, departments, academic years |
| 3 | Courses | Courses, subjects, semesters |
| 4 | Students | Batches, sections, student CRUD |
| 5 | Staff | Staff CRUD, subject allocations |
| 6 | Timetable | Visual weekly timetable grid |
| 7 | Marks | Exams, bulk mark entry, results, GPA |
| 8 | Attendance | Bulk attendance, summary, % tracking |
| 9 | Fees | Fee structures, payments, scholarships |
| 10 | Reports | Attendance/marks/fee reports + CSV export |
| 11 | AIRA | AI assistant with MCP tool bridge |
| 12 | Notifications | Parent notifications via email/SMS/WhatsApp |

---

## 🛠️ Development

### Running in Development Mode

```powershell
# Backend (with auto-reload)
cd Main\Backend
.venv\Scripts\activate
python run.py
```

### API Base URL
All API endpoints are prefixed with `/api`:
- Auth: `POST /api/auth/login`
- Students: `GET /api/students/`
- Attendance: `POST /api/attendance/`
- etc.

---

## 🎨 Theming

The app supports **dark and light themes** toggled via the 🌙/☀️ button in the header. Theme preference is saved in `localStorage`.

CSS custom properties are defined in `assets/css/main.css` under `:root` (light) and `[data-theme="dark"]`.

---

## 📝 License

MIT License — Free to use and modify.

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

1. Start **XAMPP** and ensure MySQL is running on port `3306`.
2. Open **phpMyAdmin** (`http://localhost/phpmyadmin`) or MySQL CLI.
3. Run the schema:
   ```sql
   source C:/xampp/htdocs/management-system/Main/Backend/database/schema.sql
   ```
4. Run the seed data:
   ```sql
   source C:/xampp/htdocs/management-system/Main/Backend/database/seed.sql
   ```

---

### 2. Backend Setup

```powershell
# Navigate to backend
cd C:\xampp\htdocs\management-system\Main\Backend

# Create virtual environment using uv
uv venv

# Activate virtual environment
.venv\Scripts\activate

# Install dependencies using uv
uv pip install -r requirements.txt

# Copy and configure environment
copy .env.example .env
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

Since the frontend uses plain HTML/JS, serve it via XAMPP Apache:

1. Ensure XAMPP Apache is running.
2. Open your browser and navigate to:
   ```
   http://localhost/management-system/Main/Frontend/login.html
   ```

**Default Login:**
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

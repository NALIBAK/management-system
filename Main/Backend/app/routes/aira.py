from flask import Blueprint, request
from app.db import query, execute
from app.utils.auth import login_required
from app.utils.response import success, error
import requests as http_requests
import json

aira_bp = Blueprint("aira", __name__)

# MCP Tool Definitions
MCP_TOOLS = [
    {
        "name": "get_student_info",
        "description": "Retrieve student details by ID, name, or registration number",
        "inputSchema": {
            "type": "object",
            "properties": {
                "identifier": {"type": "string", "description": "Student ID, name, or reg number"}
            },
            "required": ["identifier"]
        }
    },
    {
        "name": "get_attendance_summary",
        "description": "Get attendance percentage for students in a section or for a specific student",
        "inputSchema": {
            "type": "object",
            "properties": {
                "section_id": {"type": "integer"},
                "student_id": {"type": "integer"},
                "threshold": {"type": "number", "description": "Filter students below this percentage"}
            }
        }
    },
    {
        "name": "update_attendance",
        "description": "Update attendance status for a student on a specific date",
        "inputSchema": {
            "type": "object",
            "properties": {
                "student_id": {"type": "integer"},
                "subject_id": {"type": "integer"},
                "date": {"type": "string", "format": "date"},
                "status": {"type": "string", "enum": ["P", "A", "OD"]}
            },
            "required": ["student_id", "subject_id", "date", "status"]
        }
    },
    {
        "name": "get_marks",
        "description": "Get marks for a student or an exam",
        "inputSchema": {
            "type": "object",
            "properties": {
                "student_id": {"type": "integer"},
                "exam_id": {"type": "integer"}
            }
        }
    },
    {
        "name": "get_fee_balance",
        "description": "Get fee balance for a student",
        "inputSchema": {
            "type": "object",
            "properties": {
                "student_id": {"type": "integer"},
                "academic_year_id": {"type": "integer"}
            },
            "required": ["student_id", "academic_year_id"]
        }
    },
    {
        "name": "get_department_summary",
        "description": "Get summary statistics for all departments",
        "inputSchema": {"type": "object", "properties": {}}
    }
]

def execute_tool(tool_name: str, tool_args: dict, user: dict) -> dict:
    """Execute an MCP tool call and return the result."""
    try:
        if tool_name == "get_student_info":
            identifier = tool_args.get("identifier", "")
            result = query("""SELECT st.*, s.name as section_name, c.name as course_name
                              FROM student st JOIN section s ON st.section_id=s.section_id
                              JOIN course c ON st.course_id=c.course_id
                              WHERE st.student_id=%s OR st.reg_number=%s OR st.name LIKE %s""",
                           (identifier, identifier, f"%{identifier}%"))
            return {"success": True, "data": result}

        elif tool_name == "get_attendance_summary":
            sql = """SELECT a.student_id, st.name, st.roll_number, sub.name as subject,
                     COUNT(*) as total, SUM(CASE WHEN a.status='P' THEN 1 ELSE 0 END) as present,
                     ROUND(SUM(CASE WHEN a.status='P' THEN 1 ELSE 0 END)*100.0/COUNT(*),2) as pct
                     FROM attendance a JOIN student st ON a.student_id=st.student_id
                     JOIN subject sub ON a.subject_id=sub.subject_id WHERE 1=1"""
            params = []
            if tool_args.get("section_id"):
                sql += " AND a.section_id=%s"; params.append(tool_args["section_id"])
            if tool_args.get("student_id"):
                sql += " AND a.student_id=%s"; params.append(tool_args["student_id"])
            sql += " GROUP BY a.student_id, a.subject_id"
            if tool_args.get("threshold"):
                sql += " HAVING pct < %s"; params.append(tool_args["threshold"])
            return {"success": True, "data": query(sql, params)}

        elif tool_name == "get_marks":
            sql = """SELECT m.*, st.name, st.roll_number, e.exam_name, sub.name as subject
                     FROM mark m JOIN student st ON m.student_id=st.student_id
                     JOIN exam e ON m.exam_id=e.exam_id JOIN subject sub ON e.subject_id=sub.subject_id WHERE 1=1"""
            params = []
            if tool_args.get("student_id"):
                sql += " AND m.student_id=%s"; params.append(tool_args["student_id"])
            if tool_args.get("exam_id"):
                sql += " AND m.exam_id=%s"; params.append(tool_args["exam_id"])
            return {"success": True, "data": query(sql, params)}

        elif tool_name == "get_fee_balance":
            from app.routes.fees import get_balance
            # Inline the balance calculation
            student_id = tool_args["student_id"]
            ay_id = tool_args["academic_year_id"]
            total_due = query("SELECT COALESCE(SUM(fs.total_amount),0) as d FROM fee_structure fs JOIN student st ON st.course_id=fs.course_id WHERE st.student_id=%s AND fs.academic_year_id=%s", (student_id, ay_id), fetchone=True)
            total_paid = query("SELECT COALESCE(SUM(amount_paid),0) as p FROM fee_payment WHERE student_id=%s AND academic_year_id=%s", (student_id, ay_id), fetchone=True)
            return {"success": True, "data": {"balance": float(total_due["d"]) - float(total_paid["p"])}}

        elif tool_name == "get_department_summary":
            result = query("""SELECT d.name, COUNT(DISTINCT st.student_id) as students,
                              COUNT(DISTINCT s.staff_id) as staff FROM department d
                              LEFT JOIN course c ON c.department_id=d.department_id
                              LEFT JOIN student st ON st.course_id=c.course_id
                              LEFT JOIN staff s ON s.department_id=d.department_id
                              GROUP BY d.department_id""")
            return {"success": True, "data": result}

        else:
            return {"success": False, "error": f"Unknown tool: {tool_name}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def _get_db_context() -> str:
    """Query the database for a real-time snapshot to inject into the AIRA system prompt."""
    try:
        students = query("SELECT COUNT(*) as c FROM student WHERE status='active'", fetchone=True)
        staff    = query("SELECT COUNT(*) as c FROM staff WHERE status='active'", fetchone=True)
        courses  = query("SELECT COUNT(*) as c FROM course", fetchone=True)
        depts    = query("SELECT COUNT(*) as c FROM department", fetchone=True)
        subjects = query("SELECT COUNT(*) as c FROM subject", fetchone=True)

        dept_list  = query("SELECT name, code FROM department ORDER BY name")
        course_list = query("SELECT name, code, degree_type FROM course ORDER BY name")
        staff_list  = query("SELECT name, designation, d.name as dept FROM staff s LEFT JOIN department d ON s.department_id=d.department_id WHERE s.status='active' ORDER BY s.name")
        student_list = query("SELECT name, reg_number, roll_number FROM student WHERE status='active' ORDER BY name")
        subject_list = query("SELECT s.name, s.code, s.semester_number, c.name as course FROM subject s JOIN course c ON s.course_id=c.course_id ORDER BY c.name, s.semester_number")

        fee_total = query("SELECT COALESCE(SUM(amount_paid),0) as total FROM fee_payment", fetchone=True)
        att_avg   = query("""SELECT ROUND(AVG(pct),2) as avg FROM (
            SELECT ROUND(SUM(CASE WHEN status='P' THEN 1 ELSE 0 END)*100.0/COUNT(*),2) as pct
            FROM attendance GROUP BY student_id, subject_id HAVING COUNT(*)>0) x""", fetchone=True)

        ctx = f"""
=== LIVE DATABASE SNAPSHOT (use ONLY these facts to answer questions) ===

COUNTS:
- Active Students: {students['c']}
- Active Staff: {staff['c']}
- Courses: {courses['c']}
- Departments: {depts['c']}
- Subjects: {subjects['c']}
- Total Fees Collected: ₹{float(fee_total['total']):,.2f}
- Overall Avg Attendance: {att_avg['avg'] if att_avg['avg'] else 'N/A'}%

DEPARTMENTS ({depts['c']}):
""" + "\n".join(f"  • {d['name']} [{d['code']}]" for d in dept_list) + """

COURSES:
""" + "\n".join(f"  • {c['name']} ({c['code']}) — {c['degree_type']}" for c in course_list) + """

STAFF:
""" + "\n".join(f"  • {s['name']} — {s['designation']} ({s['dept'] or 'N/A'})" for s in staff_list) + """

STUDENTS:
""" + "\n".join(f"  • {s['name']} (Reg: {s['reg_number']}, Roll: {s['roll_number']})" for s in student_list) + """

SUBJECTS:
""" + "\n".join(f"  • {s['name']} [{s['code']}] — Sem {s['semester_number']}, Course: {s['course']}" for s in subject_list) + """

=== END OF DATABASE SNAPSHOT ===
IMPORTANT: Answer ONLY from the data above. Do NOT invent, guess, or use prior knowledge about students, staff, or college data. If something is not in the snapshot, say "No data available for that yet."
"""
        return ctx
    except Exception as e:
        return f"\n[DB context unavailable: {str(e)}]\n"


@aira_bp.route("/chat", methods=["POST"])
@login_required
def chat():
    data = request.get_json()
    message = data.get("message", "")
    conversation_id = data.get("conversation_id")
    page_context = data.get("page_context", "")
    user = request.current_user

    if not message:
        return error("Message is required")

    # Get or create conversation
    if not conversation_id:
        from datetime import datetime, timedelta
        expires = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
        conversation_id = execute("""INSERT INTO aira_conversation (user_id, title, page_context, expires_at)
                                     VALUES (%s,%s,%s,%s)""",
                                  (user["user_id"], message[:50], page_context, expires))

    # Save user message
    execute("INSERT INTO aira_message (conversation_id, role, content) VALUES (%s,'user',%s)",
            (conversation_id, message))

    # Get LLM config
    llm_config = query("SELECT * FROM llm_config LIMIT 1", fetchone=True)

    # Fetch live database snapshot — this ensures the LLM answers from real data
    db_context = _get_db_context()

    # Build system prompt with injected DB facts
    system_prompt = f"""You are AIRA, an AI Research Assistant for a College Management System.
Current user role: {user['role']}. Page context: {page_context}.

{db_context}

INSTRUCTIONS:
- Always answer questions about students, staff, departments, courses, subjects, attendance, and fees using ONLY the database snapshot above.
- For write/update/delete operations, always confirm with the user first.
- Respond concisely, helpfully, and in markdown where useful.
- If unsure or data is absent from the snapshot, say so honestly."""

    # Get conversation history
    history = query("SELECT role, content FROM aira_message WHERE conversation_id=%s ORDER BY created_at",
                    (conversation_id,))
    messages = [{"role": h["role"], "content": h["content"]} for h in history]

    # For simple keyword queries, use smart fallback (instant, no LLM latency)
    msg_lower = message.lower().strip()
    simple_keywords = [
        "how many student", "how many staff", "how many department", "how many course",
        "how many subject", "list student", "list staff", "list department", "list course",
        "show student", "show staff", "show department", "show course",
        "total student", "total staff", "total fee", "fee collected",
        "overall attendance", "department summary", "dept summary",
        "what can you do", "help", "commands"
    ]
    is_simple = any(k in msg_lower for k in simple_keywords)

    ai_response = ""
    tool_calls_made = []

    try:
        if is_simple:
            # Fast path: use smart fallback which queries DB directly
            ai_response = _smart_fallback(message, user)
        elif llm_config and llm_config.get("api_key_encrypted"):
            # Gemini API (with DB context injected in system prompt)
            ai_response = _call_gemini(llm_config, system_prompt, messages, MCP_TOOLS)
        else:
            # Ollama (with DB context injected in system prompt)
            ollama_resp = _call_ollama(system_prompt, messages)
            if "Ollama is not available" in ollama_resp or "Error:" in ollama_resp:
                ai_response = _smart_fallback(message, user)
            else:
                ai_response = ollama_resp
    except Exception as e:
        ai_response = _smart_fallback(message, user)

    # Save assistant response
    execute("INSERT INTO aira_message (conversation_id, role, content) VALUES (%s,'assistant',%s)",
            (conversation_id, ai_response))

    return success({
        "conversation_id": conversation_id,
        "response": ai_response,
        "tool_calls": tool_calls_made
    })




def _smart_fallback(message: str, user: dict) -> str:
    """Rule-based smart fallback that queries the DB to answer common questions."""
    msg = message.lower().strip()
    
    try:
        # Student queries
        if any(k in msg for k in ["how many student", "student count", "total student", "number of student"]):
            result = query("SELECT COUNT(*) as count FROM student WHERE status='active'", fetchone=True)
            count = result["count"] if result else 0
            return f"📊 There are currently **{count} active students** enrolled in the college."

        if any(k in msg for k in ["list student", "all student", "show student"]):
            students = query("SELECT name, reg_number, status FROM student ORDER BY name LIMIT 10")
            if not students:
                return "No students found in the database yet."
            lines = [f"• {s['name']} ({s['reg_number']}) — {s['status']}" for s in students]
            return f"📋 **Students** (showing up to 10):\n" + "\n".join(lines)

        # Department queries
        if any(k in msg for k in ["how many department", "department count", "total department"]):
            result = query("SELECT COUNT(*) as count FROM department", fetchone=True)
            return f"🏫 There are **{result['count']} departments** in the college."

        if any(k in msg for k in ["list department", "all department", "show department"]):
            depts = query("SELECT name, code FROM department ORDER BY name")
            if not depts:
                return "No departments found."
            lines = [f"• {d['name']} ({d['code']})" for d in depts]
            return "🏫 **Departments:**\n" + "\n".join(lines)

        # Staff queries
        if any(k in msg for k in ["how many staff", "staff count", "total staff", "how many teacher", "how many faculty"]):
            result = query("SELECT COUNT(*) as count FROM staff WHERE status='active'", fetchone=True)
            return f"👨‍🏫 There are **{result['count']} active staff members** in the college."

        if any(k in msg for k in ["list staff", "all staff", "show staff"]):
            staff = query("SELECT name, designation FROM staff WHERE status='active' ORDER BY name LIMIT 10")
            if not staff:
                return "No staff found."
            lines = [f"• {s['name']} — {s['designation']}" for s in staff]
            return "👨‍🏫 **Staff Members:**\n" + "\n".join(lines)

        # Course queries
        if any(k in msg for k in ["how many course", "course count", "total course"]):
            result = query("SELECT COUNT(*) as count FROM course", fetchone=True)
            return f"📚 There are **{result['count']} courses** offered by the college."

        if any(k in msg for k in ["list course", "all course", "show course"]):
            courses = query("SELECT name, code, degree_type FROM course ORDER BY name")
            if not courses:
                return "No courses found."
            lines = [f"• {c['name']} ({c['code']}) — {c['degree_type']}" for c in courses]
            return "📚 **Courses:**\n" + "\n".join(lines)

        # Subject queries
        if any(k in msg for k in ["how many subject", "subject count", "total subject"]):
            result = query("SELECT COUNT(*) as count FROM subject", fetchone=True)
            return f"📖 There are **{result['count']} subjects** in the curriculum."

        # Attendance queries
        if "attendance" in msg and any(k in msg for k in ["average", "overall", "summary", "how is"]):
            result = query("""SELECT ROUND(AVG(pct), 2) as avg_attendance FROM (
                SELECT ROUND(SUM(CASE WHEN status='P' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as pct
                FROM attendance GROUP BY student_id, subject_id
            ) as sub""", fetchone=True)
            avg = result["avg_attendance"] if result and result["avg_attendance"] else "N/A"
            return f"📅 The **overall average attendance** across all students is **{avg}%**."

        # Fee queries
        if any(k in msg for k in ["total fee", "fee collected", "fee payment"]):
            result = query("SELECT COALESCE(SUM(amount_paid), 0) as total FROM fee_payment", fetchone=True)
            total = float(result["total"]) if result else 0
            return f"💰 Total fees collected so far: **₹{total:,.2f}**"

        # Department summary
        if "department summary" in msg or "dept summary" in msg:
            result = execute_tool("get_department_summary", {}, user)
            if result.get("success") and result.get("data"):
                lines = [f"• **{d['name']}**: {d['students']} students, {d['staff']} staff" for d in result["data"]]
                return "🏫 **Department Summary:**\n" + "\n".join(lines)

        # Help
        if any(k in msg for k in ["help", "what can you do", "what can you", "capabilities", "commands"]):
            return """👋 Hi! I'm **AIRA**, your AI assistant for the College Management System. Here's what I can help you with:

📊 **Student Info**: "How many students are there?", "List all students"
🏫 **Departments**: "How many departments?", "List departments"  
👨‍🏫 **Staff**: "How many staff members?", "List staff"
📚 **Courses**: "How many courses?", "List courses"
📖 **Subjects**: "How many subjects?"
📅 **Attendance**: "What is the overall attendance?"
💰 **Fees**: "Total fees collected?"
📊 **Reports**: "Department summary"

> 💡 **Tip**: For more advanced queries, configure a Gemini API key in Settings → LLM Config."""

        # Default
        return f"""🤖 I understood your question: *"{message}"*

I'm currently running in **built-in mode** (no external LLM configured). I can answer common data queries about students, staff, courses, departments, attendance, and fees.

Try asking:
- "How many students are there?"
- "List all departments"
- "How many staff members?"
- "What is the overall attendance?"

For full AI capabilities, configure a **Gemini API key** in Settings → LLM Config."""

    except Exception as e:
        return f"⚠️ Sorry, I encountered an error while processing your query: {str(e)}"

def _call_ollama(system_prompt: str, messages: list) -> str:
    try:
        payload = {
            "model": "gemma3",
            "messages": [{"role": "system", "content": system_prompt}] + messages,
            "stream": False
        }
        resp = http_requests.post("http://localhost:11434/api/chat", json=payload, timeout=120)
        resp.raise_for_status()
        return resp.json()["message"]["content"]
    except Exception as e:
        return f"Ollama is not available. Please start Ollama or configure a Gemini API key. Error: {str(e)}"

def _call_gemini(config: dict, system_prompt: str, messages: list, tools: list) -> str:
    try:
        api_key = config["api_key_encrypted"]  # In production, decrypt this
        model = config.get("selected_model", "gemini-1.5-flash")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        contents = []
        for m in messages:
            role = "user" if m["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": m["content"]}]})
        payload = {
            "system_instruction": {"parts": [{"text": system_prompt}]},
            "contents": contents
        }
        resp = http_requests.post(url, json=payload, timeout=60)
        resp.raise_for_status()
        return resp.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        return f"Gemini API error: {str(e)}"

@aira_bp.route("/tools", methods=["GET"])
@login_required
def get_tools():
    return success(MCP_TOOLS)

@aira_bp.route("/execute-tool", methods=["POST"])
@login_required
def run_tool():
    data = request.get_json()
    tool_name = data.get("tool_name")
    tool_args = data.get("args", {})
    result = execute_tool(tool_name, tool_args, request.current_user)
    # Log the action
    execute("""INSERT INTO aira_action_log (user_id, action_type, entity_type, action_details, status)
               VALUES (%s,%s,%s,%s,%s)""",
            (request.current_user["user_id"], "tool_call", tool_name,
             json.dumps({"args": tool_args, "result_count": len(result.get("data", []))}),
             "success" if result["success"] else "error"))
    return success(result)

@aira_bp.route("/conversations", methods=["GET"])
@login_required
def get_conversations():
    convs = query("""SELECT * FROM aira_conversation WHERE user_id=%s AND expires_at > NOW()
                     ORDER BY updated_at DESC LIMIT 20""",
                  (request.current_user["user_id"],))
    return success(convs)

@aira_bp.route("/config", methods=["GET"])
@login_required
def get_config():
    config = query("SELECT config_id, provider, selected_model, fallback_provider, fallback_model, temperature, max_tokens FROM llm_config LIMIT 1", fetchone=True)
    return success(config)

@aira_bp.route("/config", methods=["POST"])
@login_required
def save_config():
    data = request.get_json()
    existing = query("SELECT config_id FROM llm_config LIMIT 1", fetchone=True)
    if existing:
        execute("""UPDATE llm_config SET provider=%s, api_key_encrypted=%s, selected_model=%s,
                   fallback_provider=%s, fallback_model=%s, temperature=%s, max_tokens=%s, updated_at=NOW()
                   WHERE config_id=%s""",
                (data.get("provider"), data.get("api_key"), data.get("selected_model"),
                 data.get("fallback_provider", "ollama"), data.get("fallback_model", "llama3.2"),
                 data.get("temperature", 0.7), data.get("max_tokens", 2048), existing["config_id"]))
    else:
        execute("""INSERT INTO llm_config (provider, api_key_encrypted, selected_model, fallback_provider, fallback_model, temperature, max_tokens)
                   VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                (data.get("provider"), data.get("api_key"), data.get("selected_model"),
                 data.get("fallback_provider", "ollama"), data.get("fallback_model", "llama3.2"),
                 data.get("temperature", 0.7), data.get("max_tokens", 2048)))
    return success(message="LLM configuration saved")

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
    },
    {
        "name": "generate_student_profile_report",
        "description": "Generate student profile report with name, reg no, CGPA, course, department",
        "inputSchema": {
            "type": "object",
            "properties": {
                "student_id": {"type": "integer"},
                "section_id": {"type": "integer"},
                "department_id": {"type": "integer"}
            }
        }
    },
    {
        "name": "generate_fee_structure_report",
        "description": "Generate fee structure report showing breakdown by course, category, semester",
        "inputSchema": {
            "type": "object",
            "properties": {
                "course_id": {"type": "integer"},
                "academic_year_id": {"type": "integer"},
                "fee_category_id": {"type": "integer"}
            }
        }
    },
    {
        "name": "generate_eligibility_report",
        "description": "Generate eligibility criteria report showing match/unmatch status per student",
        "inputSchema": {
            "type": "object",
            "properties": {
                "student_id": {"type": "integer"},
                "section_id": {"type": "integer"},
                "criteria_id": {"type": "integer"}
            }
        }
    },
    {
        "name": "generate_category_wise_report",
        "description": "Generate category-wise student report (centac/management/regular)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "department_id": {"type": "integer"},
                "course_id": {"type": "integer"},
                "batch_id": {"type": "integer"}
            }
        }
    },
    {
        "name": "generate_scholarship_report",
        "description": "Generate caste/community-wise scholarship report",
        "inputSchema": {
            "type": "object",
            "properties": {
                "department_id": {"type": "integer"},
                "academic_year_id": {"type": "integer"},
                "caste_community": {"type": "string"}
            }
        }
    },
    {
        "name": "generate_extracurricular_report",
        "description": "Generate extracurricular activities report (technical and non-technical)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "student_id": {"type": "integer"},
                "section_id": {"type": "integer"},
                "department_id": {"type": "integer"},
                "activity_type": {"type": "string", "enum": ["technical", "non_technical"]}
            }
        }
    },
    {
        "name": "generate_attendance_report",
        "description": "Generate detailed attendance report with flexible filters",
        "inputSchema": {
            "type": "object",
            "properties": {
                "section_id": {"type": "integer"},
                "student_id": {"type": "integer"},
                "department_id": {"type": "integer"},
                "subject_id": {"type": "integer"},
                "date_from": {"type": "string", "format": "date"},
                "date_to": {"type": "string", "format": "date"}
            }
        }
    },
    {
        "name": "generate_marks_report",
        "description": "Generate detailed marks report with flexible filters",
        "inputSchema": {
            "type": "object",
            "properties": {
                "section_id": {"type": "integer"},
                "student_id": {"type": "integer"},
                "department_id": {"type": "integer"},
                "subject_id": {"type": "integer"},
                "exam_type_id": {"type": "integer"}
            }
        }
    }
]

def execute_tool(tool_name: str, tool_args: dict, user: dict) -> dict:
    """Execute an MCP tool call and return the result."""
    result = None
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

        elif tool_name == "generate_student_profile_report":
            sql = """SELECT st.student_id, st.name, st.reg_number, st.roll_number,
                     st.student_category, st.caste_community,
                     c.name as course_name, d.name as department_name, sec.name as section_name,
                     COALESCE(sr.cgpa, 0) as cgpa, MAX(sem.semester_number) as latest_semester
                     FROM student st
                     JOIN course c ON st.course_id=c.course_id
                     JOIN department d ON c.department_id=d.department_id
                     JOIN section sec ON st.section_id=sec.section_id
                     LEFT JOIN semester_result sr ON sr.student_id=st.student_id
                     LEFT JOIN semester sem ON sr.semester_id=sem.semester_id
                     WHERE st.status='active'"""
            params = []
            if tool_args.get("student_id"):
                sql += " AND st.student_id=%s"; params.append(tool_args["student_id"])
            if tool_args.get("section_id"):
                sql += " AND st.section_id=%s"; params.append(tool_args["section_id"])
            if tool_args.get("department_id"):
                sql += " AND c.department_id=%s"; params.append(tool_args["department_id"])
            sql += " GROUP BY st.student_id ORDER BY st.name"
            return {"success": True, "data": query(sql, params)}

        elif tool_name == "generate_fee_structure_report":
            sql = """SELECT c.name as course_name, fc.name as fee_category,
                     fs.semester_number, fs.total_amount, ay.year_label
                     FROM fee_structure fs
                     JOIN course c ON fs.course_id=c.course_id
                     JOIN fee_category fc ON fs.fee_category_id=fc.fee_category_id
                     JOIN academic_year ay ON fs.academic_year_id=ay.academic_year_id
                     WHERE 1=1"""
            params = []
            if tool_args.get("course_id"):
                sql += " AND fs.course_id=%s"; params.append(tool_args["course_id"])
            if tool_args.get("academic_year_id"):
                sql += " AND fs.academic_year_id=%s"; params.append(tool_args["academic_year_id"])
            if tool_args.get("fee_category_id"):
                sql += " AND fs.fee_category_id=%s"; params.append(tool_args["fee_category_id"])
            sql += " ORDER BY c.name, fs.semester_number"
            return {"success": True, "data": query(sql, params)}

        elif tool_name == "generate_eligibility_report":
            sql = """SELECT st.name as student_name, st.reg_number,
                     ec.name as criteria_name, ec.criteria_type, ec.threshold_value,
                     se.status as eligibility_status, se.evaluated_value, se.remarks
                     FROM student_eligibility se
                     JOIN student st ON se.student_id=st.student_id
                     JOIN eligibility_criteria ec ON se.criteria_id=ec.criteria_id
                     WHERE st.status='active'"""
            params = []
            if tool_args.get("student_id"):
                sql += " AND se.student_id=%s"; params.append(tool_args["student_id"])
            if tool_args.get("section_id"):
                sql += " AND st.section_id=%s"; params.append(tool_args["section_id"])
            if tool_args.get("criteria_id"):
                sql += " AND se.criteria_id=%s"; params.append(tool_args["criteria_id"])
            sql += " ORDER BY st.name, ec.name"
            return {"success": True, "data": query(sql, params)}

        elif tool_name == "generate_category_wise_report":
            sql = """SELECT st.student_category, c.name as course_name, d.name as department_name,
                     COUNT(*) as student_count
                     FROM student st
                     JOIN course c ON st.course_id=c.course_id
                     JOIN department d ON c.department_id=d.department_id
                     WHERE st.status='active'"""
            params = []
            if tool_args.get("department_id"):
                sql += " AND c.department_id=%s"; params.append(tool_args["department_id"])
            if tool_args.get("course_id"):
                sql += " AND st.course_id=%s"; params.append(tool_args["course_id"])
            if tool_args.get("batch_id"):
                sql += " AND st.batch_id=%s"; params.append(tool_args["batch_id"])
            sql += " GROUP BY st.student_category, c.course_id ORDER BY d.name, c.name"
            return {"success": True, "data": query(sql, params)}

        elif tool_name == "generate_scholarship_report":
            sql = """SELECT st.caste_community, st.name as student_name, st.reg_number,
                     c.name as course_name, sch.scholarship_name, sch.amount, sch.status as scholarship_status
                     FROM scholarship sch
                     JOIN student st ON sch.student_id=st.student_id
                     JOIN course c ON st.course_id=c.course_id
                     JOIN department d ON c.department_id=d.department_id
                     JOIN academic_year ay ON sch.academic_year_id=ay.academic_year_id
                     WHERE 1=1"""
            params = []
            if tool_args.get("department_id"):
                sql += " AND c.department_id=%s"; params.append(tool_args["department_id"])
            if tool_args.get("academic_year_id"):
                sql += " AND sch.academic_year_id=%s"; params.append(tool_args["academic_year_id"])
            if tool_args.get("caste_community"):
                sql += " AND st.caste_community=%s"; params.append(tool_args["caste_community"])
            sql += " ORDER BY st.caste_community, st.name"
            return {"success": True, "data": query(sql, params)}

        elif tool_name == "generate_extracurricular_report":
            sql = """SELECT st.name as student_name, st.reg_number,
                     ea.title, ea.activity_type, ea.category, ea.event_date, ea.achievement,
                     c.name as course_name, d.name as department_name
                     FROM extracurricular_activity ea
                     JOIN student st ON ea.student_id=st.student_id
                     JOIN course c ON st.course_id=c.course_id
                     JOIN department d ON c.department_id=d.department_id
                     WHERE st.status='active'"""
            params = []
            if tool_args.get("student_id"):
                sql += " AND ea.student_id=%s"; params.append(tool_args["student_id"])
            if tool_args.get("section_id"):
                sql += " AND st.section_id=%s"; params.append(tool_args["section_id"])
            if tool_args.get("department_id"):
                sql += " AND c.department_id=%s"; params.append(tool_args["department_id"])
            if tool_args.get("activity_type"):
                sql += " AND ea.activity_type=%s"; params.append(tool_args["activity_type"])
            sql += " ORDER BY ea.event_date DESC, st.name"
            return {"success": True, "data": query(sql, params)}

        elif tool_name == "generate_attendance_report":
            sql = """SELECT st.name as student_name, st.reg_number, sub.name as subject_name,
                     d.name as department_name, sec.name as section_name,
                     COUNT(*) as total_classes,
                     SUM(CASE WHEN a.status='P' THEN 1 ELSE 0 END) as present,
                     ROUND(SUM(CASE WHEN a.status='P' THEN 1 ELSE 0 END)*100.0/COUNT(*),2) as pct
                     FROM attendance a
                     JOIN student st ON a.student_id=st.student_id
                     JOIN subject sub ON a.subject_id=sub.subject_id
                     JOIN section sec ON a.section_id=sec.section_id
                     JOIN course c ON st.course_id=c.course_id
                     JOIN department d ON c.department_id=d.department_id
                     WHERE 1=1"""
            params = []
            if tool_args.get("section_id"):
                sql += " AND a.section_id=%s"; params.append(tool_args["section_id"])
            if tool_args.get("student_id"):
                sql += " AND a.student_id=%s"; params.append(tool_args["student_id"])
            if tool_args.get("department_id"):
                sql += " AND c.department_id=%s"; params.append(tool_args["department_id"])
            if tool_args.get("subject_id"):
                sql += " AND a.subject_id=%s"; params.append(tool_args["subject_id"])
            if tool_args.get("date_from"):
                sql += " AND a.attendance_date >= %s"; params.append(tool_args["date_from"])
            if tool_args.get("date_to"):
                sql += " AND a.attendance_date <= %s"; params.append(tool_args["date_to"])
            sql += " GROUP BY a.student_id, a.subject_id ORDER BY d.name, st.name"
            return {"success": True, "data": query(sql, params)}

        elif tool_name == "generate_marks_report":
            sql = """SELECT st.name as student_name, st.reg_number,
                     e.exam_name, et.name as exam_type, sub.name as subject_name,
                     d.name as department_name, sec.name as section_name,
                     m.marks_obtained, e.max_marks, e.passing_marks,
                     CASE WHEN m.is_absent=1 THEN 'absent'
                          WHEN m.marks_obtained >= e.passing_marks THEN 'pass' ELSE 'fail' END as result_status
                     FROM mark m
                     JOIN exam e ON m.exam_id=e.exam_id
                     JOIN exam_type et ON e.exam_type_id=et.exam_type_id
                     JOIN subject sub ON e.subject_id=sub.subject_id
                     JOIN section sec ON e.section_id=sec.section_id
                     JOIN student st ON m.student_id=st.student_id
                     JOIN course c ON st.course_id=c.course_id
                     JOIN department d ON c.department_id=d.department_id
                     WHERE 1=1"""
            params = []
            if tool_args.get("section_id"):
                sql += " AND e.section_id=%s"; params.append(tool_args["section_id"])
            if tool_args.get("student_id"):
                sql += " AND m.student_id=%s"; params.append(tool_args["student_id"])
            if tool_args.get("department_id"):
                sql += " AND c.department_id=%s"; params.append(tool_args["department_id"])
            if tool_args.get("subject_id"):
                sql += " AND e.subject_id=%s"; params.append(tool_args["subject_id"])
            if tool_args.get("exam_type_id"):
                sql += " AND e.exam_type_id=%s"; params.append(tool_args["exam_type_id"])
            sql += " ORDER BY d.name, st.name, sub.name"
            return {"success": True, "data": query(sql, params)}

        elif tool_name == "update_attendance":
            # Write operation — requires confirmation, do NOT execute directly
            student_id = tool_args.get("student_id")
            subject_id = tool_args.get("subject_id")
            date = tool_args.get("date")
            att_status = tool_args.get("status", "P")
            # Look up names for the preview
            student = query("SELECT name, reg_number FROM student WHERE student_id=%s", (student_id,), fetchone=True)
            subject = query("SELECT name FROM subject WHERE subject_id=%s", (subject_id,), fetchone=True)
            student_name = student["name"] if student else f"ID:{student_id}"
            subject_name = subject["name"] if subject else f"ID:{subject_id}"
            status_label = {"P": "Present", "A": "Absent", "OD": "On Duty"}.get(att_status, att_status)
            # Store as pending action
            action_id = execute(
                """INSERT INTO aira_action_log
                   (user_id, action_type, entity_type, action_details, status)
                   VALUES (%s, 'write', 'attendance', %s, 'pending')""",
                (user["user_id"], json.dumps(tool_args))
            )
            return {
                "success": True,
                "needs_confirmation": True,
                "action_id": action_id,
                "preview": f"Mark **{student_name}** as **{status_label}** for **{subject_name}** on **{date}**"
            }

        else:
            return {"success": False, "error": f"Unknown tool: {tool_name}"}
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        # Log every tool execution to aira_action_log
        if result is not None:
            try:
                execute(
                    """INSERT INTO aira_action_log (user_id, action_type, entity_type, action_details, status)
                       VALUES (%s, %s, %s, %s, %s)""",
                    (user["user_id"], "tool_call", tool_name,
                     json.dumps({"args": tool_args}),
                     "success" if result.get("success") else "error")
                )
            except Exception:
                pass

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

CATEGORY DISTRIBUTION:
""" + _get_category_context() + """

=== END OF DATABASE SNAPSHOT ===
IMPORTANT: Answer ONLY from the data above. Do NOT invent, guess, or use prior knowledge about students, staff, or college data. If something is not in the snapshot, say "No data available for that yet."
"""
        return ctx
    except Exception as e:
        return f"\n[DB context unavailable: {str(e)}]\n"


def _get_category_context() -> str:
    """Get student category and caste/community distribution for context."""
    try:
        cat_dist = query("""SELECT student_category, COUNT(*) as cnt
                            FROM student WHERE status='active'
                            GROUP BY student_category""")
        caste_dist = query("""SELECT COALESCE(caste_community, 'Not Set') as community, COUNT(*) as cnt
                              FROM student WHERE status='active'
                              GROUP BY caste_community""")
        activities = query("""SELECT activity_type, COUNT(*) as cnt
                              FROM extracurricular_activity ea
                              JOIN student st ON ea.student_id=st.student_id
                              WHERE st.status='active'
                              GROUP BY activity_type""")
        criteria = query("SELECT name, criteria_type, threshold_value, comparison FROM eligibility_criteria WHERE is_active=1")
        ctx = ""
        if cat_dist:
            ctx += "  Admission Categories: " + ", ".join(f"{c['student_category']}: {c['cnt']}" for c in cat_dist) + "\n"
        if caste_dist:
            ctx += "  Caste/Community: " + ", ".join(f"{c['community']}: {c['cnt']}" for c in caste_dist) + "\n"
        if activities:
            ctx += "  Extracurricular: " + ", ".join(f"{a['activity_type']}: {a['cnt']}" for a in activities) + "\n"
        if criteria:
            ctx += "  Eligibility Criteria: " + ", ".join(f"{c['name']} ({c['criteria_type']} {c['comparison']} {c['threshold_value']})" for c in criteria) + "\n"
        return ctx if ctx else "  No category data available yet.\n"
    except:
        return "  Category data unavailable.\n"


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

    # Lazy cleanup: delete expired conversations
    try:
        execute("DELETE FROM aira_message WHERE conversation_id IN (SELECT conversation_id FROM aira_conversation WHERE expires_at < NOW())")
        execute("DELETE FROM aira_conversation WHERE expires_at < NOW()")
    except Exception:
        pass

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
        "what can you do", "help", "commands",
        # Report keywords
        "cgpa report", "student profile report", "profile report", "cgpa of",
        "fee structure", "fee breakdown", "fee report",
        "eligibility report", "eligible student", "eligibility criteria",
        "category wise", "category report", "centac student", "management student",
        "scholarship report", "caste wise", "community wise", "sc/st", "obc scholarship",
        "extracurricular", "extra curricular", "technical activit", "non technical activit",
        "attendance report", "attendance of", "attendance for",
        "marks report", "mark report", "marks of", "marks for",
        # Write actions
        "mark "
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
            ollama_model = llm_config.get("selected_model", "gemma3:1b") if llm_config else "gemma3:1b"
            ollama_resp = _call_ollama(system_prompt, messages, ollama_model)
            if "Ollama is not available" in ollama_resp or "Error:" in ollama_resp:
                ai_response = _smart_fallback(message, user)
            else:
                ai_response = ollama_resp
    except Exception as e:
        ai_response = _smart_fallback(message, user)

    # If smart fallback returned a dict (confirmation needed), return it directly
    if isinstance(ai_response, dict):
        return success({
            "conversation_id": conversation_id,
            "response": ai_response.get("preview", ""),
            "needs_confirmation": True,
            "action_id": ai_response.get("action_id"),
            "preview": ai_response.get("preview", ""),
            "tool_calls": tool_calls_made
        })

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

        # Check if message is really a report query (avoid false-matching "show student CGPA report" as "show student")
        report_keywords = ["cgpa", "profile report", "category", "eligibility", "scholarship", "extracurricular",
                           "extra curricular", "fee structure", "fee breakdown", "fee report",
                           "attendance report", "attendance for", "attendance of",
                           "marks report", "mark report", "marks for", "marks of"]
        is_report_query = any(k in msg for k in report_keywords)

        if not is_report_query and any(k in msg for k in ["list student", "all student", "show student"]):
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

        # ===== NEW REPORT SMART FALLBACKS =====

        # CGPA / Student Profile Report
        if any(k in msg for k in ["cgpa report", "student profile report", "profile report", "cgpa of"]):
            result = execute_tool("generate_student_profile_report", {}, user)
            if result.get("success") and result.get("data"):
                lines = [f"• **{s['name']}** (Reg: {s['reg_number']}) — CGPA: **{s.get('cgpa', 0)}**, Course: {s['course_name']}, Dept: {s['department_name']}" for s in result["data"]]
                return f"📊 **Student Profile / CGPA Report** ({len(result['data'])} students):\n" + "\n".join(lines)
            return "📊 No student profile data available yet."

        # Fee Structure Report
        if any(k in msg for k in ["fee structure", "fee breakdown", "fee report"]):
            result = execute_tool("generate_fee_structure_report", {}, user)
            if result.get("success") and result.get("data"):
                lines = [f"• **{f['course_name']}** — {f['fee_category']} — Sem {f['semester_number']}: ₹{float(f['total_amount']):,.0f}" for f in result["data"]]
                return f"💰 **Fee Structure Report** ({len(result['data'])} entries):\n" + "\n".join(lines)
            return "💰 No fee structure data available yet. Fee structures need to be configured in the Fees module."

        # Eligibility Report
        if any(k in msg for k in ["eligibility report", "eligible student", "eligibility criteria"]):
            result = execute_tool("generate_eligibility_report", {}, user)
            if result.get("success") and result.get("data"):
                lines = [f"• **{e['student_name']}** ({e['reg_number']}) — {e['criteria_name']}: **{e['eligibility_status'].upper()}** (Value: {e.get('evaluated_value', 'N/A')}, Threshold: {e['threshold_value']})" for e in result["data"]]
                return f"🎯 **Eligibility Report** ({len(result['data'])} evaluations):\n" + "\n".join(lines)
            return "🎯 No eligibility evaluations found yet. Use the Eligibility module to evaluate students against criteria."

        # Category-wise Report
        if any(k in msg for k in ["category wise", "category report", "centac student", "management student"]):
            result = execute_tool("generate_category_wise_report", {}, user)
            if result.get("success") and result.get("data"):
                lines = [f"• **{c.get('student_category', 'regular').upper()}** — {c['course_name']} ({c['department_name']}): **{c['student_count']} students**" for c in result["data"]]
                return f"🏷️ **Category-wise Student Report**:\n" + "\n".join(lines)
            return "🏷️ No category data available. Update student records with admission category (centac/management)."

        # Scholarship Report
        if any(k in msg for k in ["scholarship report", "caste wise", "community wise", "sc/st", "obc scholarship"]):
            result = execute_tool("generate_scholarship_report", {}, user)
            if result.get("success") and result.get("data"):
                lines = [f"• **{s['student_name']}** ({s.get('caste_community', 'N/A')}) — {s['scholarship_name']}: ₹{float(s['amount']):,.0f} [{s['scholarship_status']}]" for s in result["data"]]
                return f"🎓 **Scholarship Report** ({len(result['data'])} scholarships):\n" + "\n".join(lines)
            return "🎓 No scholarship data available yet. Add scholarships in the Fees module."

        # Extracurricular Report
        if any(k in msg for k in ["extracurricular", "extra curricular", "technical activit", "non technical activit"]):
            args = {}
            if "technical" in msg and "non" not in msg:
                args["activity_type"] = "technical"
            elif "non technical" in msg or "non-technical" in msg:
                args["activity_type"] = "non_technical"
            result = execute_tool("generate_extracurricular_report", args, user)
            if result.get("success") and result.get("data"):
                lines = [f"• **{a['student_name']}** — {a['title']} ({a['activity_type']}/{a.get('category', 'N/A')}) — {a.get('achievement', 'N/A')}" for a in result["data"]]
                return f"🏆 **Extracurricular Activities Report** ({len(result['data'])} activities):\n" + "\n".join(lines)
            return "🏆 No extracurricular activities recorded yet."

        # Attendance Report (extended)
        if any(k in msg for k in ["attendance report", "attendance of", "attendance for"]):
            result = execute_tool("generate_attendance_report", {}, user)
            if result.get("success") and result.get("data"):
                lines = [f"• **{a['student_name']}** ({a['reg_number']}) — {a['subject_name']}: {a['present']}/{a['total_classes']} (**{a['pct']}%**)" for a in result["data"]]
                return f"📅 **Attendance Report** ({len(result['data'])} records):\n" + "\n".join(lines[:20])
            return "📅 No attendance records found."

        # Marks Report (extended)
        if any(k in msg for k in ["marks report", "mark report", "marks of", "marks for"]):
            result = execute_tool("generate_marks_report", {}, user)
            if result.get("success") and result.get("data"):
                lines = [f"• **{m['student_name']}** — {m['subject_name']} ({m['exam_name']}): {m['marks_obtained']}/{m['max_marks']} [{m['result_status']}]" for m in result["data"]]
                return f"📝 **Marks Report** ({len(result['data'])} records):\n" + "\n".join(lines[:20])
            return "📝 No marks records found."

        # Attendance Write (mark present/absent)
        import re
        att_match = re.search(r'mark\s+(.+?)\s+(present|absent|od)\s+(?:for\s+)?(.+?)(?:\s+(?:on|today|for)\s+(.+))?$', msg)
        if att_match:
            student_name = att_match.group(1).strip()
            att_status = {"present": "P", "absent": "A", "od": "OD"}[att_match.group(2)]
            subject_name = att_match.group(3).strip()
            date_str = att_match.group(4).strip() if att_match.group(4) else None
            if not date_str or date_str == "today":
                from datetime import date
                date_str = date.today().isoformat()
            # Find student and subject
            student = query("SELECT student_id, name FROM student WHERE LOWER(name) LIKE %s AND status='active' LIMIT 1",
                            (f"%{student_name}%",), fetchone=True)
            subject = query("SELECT subject_id, name FROM subject WHERE LOWER(name) LIKE %s LIMIT 1",
                            (f"%{subject_name}%",), fetchone=True)
            if student and subject:
                result = execute_tool("update_attendance", {
                    "student_id": student["student_id"],
                    "subject_id": subject["subject_id"],
                    "date": date_str,
                    "status": att_status
                }, user)
                if result.get("needs_confirmation"):
                    return result  # Return the confirmation dict directly
                return "✅ Attendance request processed."
            elif not student:
                return f"❌ Could not find student matching **{student_name}**."
            else:
                return f"❌ Could not find subject matching **{subject_name}**."

        # Help
        if any(k in msg for k in ["help", "what can you do", "what can you", "capabilities", "commands"]):
            return """👋 Hi! I'm **AIRA**, your AI assistant for the College Management System. Here's what I can help you with:

📊 **Student Info**: "How many students?", "List students", "Student profile report"
🏫 **Departments**: "How many departments?", "Department summary"  
👨‍🏫 **Staff**: "How many staff members?", "List staff"
📚 **Courses**: "How many courses?", "List courses"
📖 **Subjects**: "How many subjects?"
📅 **Attendance**: "Overall attendance", "Attendance report"
💰 **Fees**: "Total fees collected?", "Fee structure report"
📝 **Marks**: "Marks report", "Show marks"

**📋 Advanced Reports:**
🎯 **Eligibility**: "Eligibility report", "Eligible students"
🏷️ **Categories**: "Category wise report", "Centac students"
🎓 **Scholarships**: "Scholarship report", "Caste wise scholarships"
🏆 **Activities**: "Extracurricular activities", "Technical activities"
📊 **CGPA**: "CGPA report", "Student profile report"
💰 **Fee Structure**: "Fee structure", "Fee breakdown"

**✏️ Write Actions (with confirmation):**
📅 **Attendance**: "Mark John present for DBMS today"

> 💡 **Tip**: For more advanced queries, configure a Gemini API key in Settings → LLM Config."""

        # Default
        return f"""🤖 I understood your question: *"{message}"*

I'm currently running in **built-in mode** (no external LLM configured). I can answer common data queries and generate reports.

Try asking:
- "Show student CGPA report"
- "Show category wise report"
- "Attendance report"
- "Eligibility report"
- "Scholarship report"
- "Fee structure report"
- "Extracurricular activities"

For full AI capabilities, configure a **Gemini API key** in Settings → LLM Config."""

    except Exception as e:
        return f"⚠️ Sorry, I encountered an error while processing your query: {str(e)}"

def _call_ollama(system_prompt: str, messages: list, model: str = "gemma3:1b") -> str:
    try:
        payload = {
            "model": model,
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


@aira_bp.route("/confirm-action", methods=["POST"])
@login_required
def confirm_action():
    """Execute a previously pending write action after user confirmation."""
    data = request.get_json()
    action_id = data.get("action_id")
    if not action_id:
        return error("action_id is required")

    # Fetch the pending action
    action = query(
        "SELECT * FROM aira_action_log WHERE action_id=%s AND status='pending' AND user_id=%s",
        (action_id, request.current_user["user_id"]), fetchone=True
    )
    if not action:
        return error("Action not found or already processed", 404)

    try:
        details = json.loads(action["action_details"])
        entity_type = action["entity_type"]

        if entity_type == "attendance":
            # Execute the attendance update
            student_id = details["student_id"]
            subject_id = details["subject_id"]
            date = details["date"]
            att_status = details.get("status", "P")
            # Check if record exists
            existing = query(
                "SELECT attendance_id FROM attendance WHERE student_id=%s AND subject_id=%s AND attendance_date=%s",
                (student_id, subject_id, date), fetchone=True
            )
            if existing:
                execute("UPDATE attendance SET status=%s WHERE attendance_id=%s",
                        (att_status, existing["attendance_id"]))
            else:
                # Need section_id and period_id — get from student context
                student = query("SELECT section_id FROM student WHERE student_id=%s", (student_id,), fetchone=True)
                section_id = student["section_id"] if student else None
                period = query("SELECT period_id FROM period_definition ORDER BY period_number LIMIT 1", fetchone=True)
                period_id = period["period_id"] if period else None
                ay = query("SELECT academic_year_id FROM academic_year WHERE is_current=1 LIMIT 1", fetchone=True)
                ay_id = ay["academic_year_id"] if ay else None
                execute(
                    """INSERT INTO attendance (student_id, subject_id, section_id, period_id,
                       academic_year_id, attendance_date, status) VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                    (student_id, subject_id, section_id, period_id, ay_id, date, att_status)
                )
            # Mark action as completed
            execute("UPDATE aira_action_log SET status='completed' WHERE action_id=%s", (action_id,))
            return success({"completed": True}, "✅ Attendance updated successfully!")
        else:
            return error(f"Unsupported action type: {entity_type}")
    except Exception as e:
        execute("UPDATE aira_action_log SET status='error' WHERE action_id=%s", (action_id,))
        return error(f"Failed to execute action: {str(e)}")


@aira_bp.route("/cancel-action", methods=["POST"])
@login_required
def cancel_action():
    """Cancel a previously pending write action."""
    data = request.get_json()
    action_id = data.get("action_id")
    if not action_id:
        return error("action_id is required")
    execute(
        "UPDATE aira_action_log SET status='cancelled' WHERE action_id=%s AND status='pending' AND user_id=%s",
        (action_id, request.current_user["user_id"])
    )
    return success(message="Action cancelled")

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
                 data.get("fallback_provider", "ollama"), data.get("fallback_model", "gemma3:1b"),
                 data.get("temperature", 0.7), data.get("max_tokens", 2048), existing["config_id"]))
    else:
        execute("""INSERT INTO llm_config (provider, api_key_encrypted, selected_model, fallback_provider, fallback_model, temperature, max_tokens)
                   VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                (data.get("provider"), data.get("api_key"), data.get("selected_model"),
                 data.get("fallback_provider", "ollama"), data.get("fallback_model", "gemma3:1b"),
                 data.get("temperature", 0.7), data.get("max_tokens", 2048)))
    return success(message="LLM configuration saved")

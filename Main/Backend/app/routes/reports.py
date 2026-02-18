from flask import Blueprint, request, send_file
from app.db import query
from app.utils.auth import login_required, roles_required
from app.utils.response import success, error
import io

reports_bp = Blueprint("reports", __name__)

@reports_bp.route("/attendance", methods=["GET"])
@login_required
def attendance_report():
    section_id = request.args.get("section_id")
    subject_id = request.args.get("subject_id")
    threshold = float(request.args.get("threshold", 75))
    sql = """SELECT a.student_id, st.name as student_name, st.roll_number,
             a.subject_id, sub.name as subject_name,
             COUNT(*) as total_classes,
             SUM(CASE WHEN a.status='P' THEN 1 ELSE 0 END) as present_count,
             ROUND(SUM(CASE WHEN a.status='P' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as percentage
             FROM attendance a
             JOIN student st ON a.student_id=st.student_id
             JOIN subject sub ON a.subject_id=sub.subject_id WHERE 1=1"""
    params = []
    if section_id:
        sql += " AND a.section_id=%s"; params.append(section_id)
    if subject_id:
        sql += " AND a.subject_id=%s"; params.append(subject_id)
    sql += " GROUP BY a.student_id, a.subject_id HAVING percentage < %s ORDER BY percentage ASC"
    params.append(threshold)
    return success(query(sql, params))

@reports_bp.route("/marks", methods=["GET"])
@login_required
def marks_report():
    section_id = request.args.get("section_id")
    semester_id = request.args.get("semester_id")
    sql = """SELECT sr.*, st.name as student_name, st.reg_number, st.roll_number,
             sem.semester_number, ay.year_label
             FROM semester_result sr
             JOIN student st ON sr.student_id=st.student_id
             JOIN semester sem ON sr.semester_id=sem.semester_id
             JOIN academic_year ay ON sr.academic_year_id=ay.academic_year_id WHERE 1=1"""
    params = []
    if section_id:
        sql += """ AND sr.student_id IN (SELECT student_id FROM student WHERE section_id=%s)"""
        params.append(section_id)
    if semester_id:
        sql += " AND sr.semester_id=%s"; params.append(semester_id)
    sql += " ORDER BY st.roll_number"
    return success(query(sql, params))

@reports_bp.route("/fee-defaulters", methods=["GET"])
@login_required
def fee_defaulters():
    ay_id = request.args.get("academic_year_id")
    dept_id = request.args.get("department_id")
    sql = """SELECT st.student_id, st.name, st.reg_number, st.roll_number,
             COALESCE(SUM(fs.total_amount), 0) as total_due,
             COALESCE(SUM(fp.amount_paid), 0) as total_paid,
             COALESCE(SUM(fs.total_amount), 0) - COALESCE(SUM(fp.amount_paid), 0) as balance
             FROM student st
             JOIN course c ON st.course_id=c.course_id
             LEFT JOIN fee_structure fs ON fs.course_id=c.course_id AND fs.academic_year_id=%s
             LEFT JOIN fee_payment fp ON fp.student_id=st.student_id AND fp.academic_year_id=%s
             WHERE st.status='active'"""
    params = [ay_id, ay_id]
    if dept_id:
        sql += " AND c.department_id=%s"; params.append(dept_id)
    sql += " GROUP BY st.student_id HAVING balance > 0 ORDER BY balance DESC"
    return success(query(sql, params))

@reports_bp.route("/department-summary", methods=["GET"])
@login_required
def department_summary():
    ay_id = request.args.get("academic_year_id")
    sql = """SELECT d.department_id, d.name as department_name,
             COUNT(DISTINCT st.student_id) as total_students,
             COUNT(DISTINCT s.staff_id) as total_staff,
             COUNT(DISTINCT c.course_id) as total_courses
             FROM department d
             LEFT JOIN course c ON c.department_id=d.department_id
             LEFT JOIN student st ON st.course_id=c.course_id AND st.status='active'
             LEFT JOIN staff s ON s.department_id=d.department_id AND s.status='active'
             GROUP BY d.department_id ORDER BY d.name"""
    return success(query(sql, []))

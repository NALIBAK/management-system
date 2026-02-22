import urllib.request
import json
import random
import sys

BASE_URL = "http://localhost:5000/api"

def make_request(method, endpoint, token, payload=None):
    url = f"{BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    data = json.dumps(payload).encode('utf-8') if payload else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"Error on {method} {url}: {e.code} - {e.read().decode('utf-8')}")
        return None

# 1. Login
login_payload = {"username": "superadmin", "password": "Admin@123"}
req = urllib.request.Request(f"{BASE_URL}/auth/login", data=json.dumps(login_payload).encode('utf-8'), headers={"Content-Type": "application/json"}, method="POST")
try:
    with urllib.request.urlopen(req) as response:
        res = json.loads(response.read().decode('utf-8'))
        token = res['data']['token']
        print("Logged in successfully.")
except Exception as e:
    print("Login failed:", e)
    sys.exit(1)

# 2. Add Departments
depts_data = [
    {"name": "Computer Science", "code": "CS", "college_id": 1},
    {"name": "Mathematics", "code": "MATH", "college_id": 1}
]
dept_ids = []
for d in depts_data:
    res = make_request("POST", "/college/departments", token, d)
    if res and res.get("success"):
        dept_ids.append(res['data']['department_id'])
        print(f"Added Department: {d['name']} (ID: {dept_ids[-1]})")
    else:
        # Fetch existing
        existing = make_request("GET", "/college/departments", token)
        for ex_d in existing.get('data', []):
            if ex_d['name'] == d['name']:
                dept_ids.append(ex_d['department_id'])
                print(f"Found existing Department: {d['name']} (ID: {ex_d['department_id']})")

if not dept_ids:
    print("No departments available. Exiting.")
    sys.exit(1)

# 3. Add Courses
courses_data = [
    {"department_id": dept_ids[0], "name": "B.Tech Computer Science", "code": "BTCS", "total_semesters": 8, "degree_type": "B.Tech"},
    {"department_id": dept_ids[1], "name": "B.Sc Mathematics", "code": "BSCM", "total_semesters": 6, "degree_type": "B.Sc"}
]
course_ids = []
for c in courses_data:
    res = make_request("POST", "/courses", token, c)
    if res and res.get("success"):
        course_ids.append(res['data']['course_id'])
        print(f"Added Course: {c['name']} (ID: {course_ids[-1]})")
    else:
        existing = make_request("GET", "/courses", token)
        for ex_c in existing.get('data', []):
            if ex_c['name'] == c['name']:
                course_ids.append(ex_c['course_id'])
                print(f"Found existing Course: {c['name']} (ID: {ex_c['course_id']})")

if not course_ids:
    print("No courses available. Exiting.")
    sys.exit(1)

# 4. Add Subjects
subjects_data = [
    {"course_id": course_ids[0], "semester": 1, "name": "Introduction to Programming", "code": "CS101", "credits": 4, "type": "theory", "department_id": dept_ids[0]},
    {"course_id": course_ids[0], "semester": 1, "name": "Data Structures", "code": "CS102", "credits": 4, "type": "theory", "department_id": dept_ids[0]},
    {"course_id": course_ids[1], "semester": 1, "name": "Calculus I", "code": "M101", "credits": 4, "type": "theory", "department_id": dept_ids[1]},
    {"course_id": course_ids[1], "semester": 1, "name": "Linear Algebra", "code": "M102", "credits": 4, "type": "theory", "department_id": dept_ids[1]}
]
subject_ids = []
for s in subjects_data:
    res = make_request("POST", "/courses/subjects", token, s)
    if res and res.get("success"):
        subject_ids.append(res['data']['subject_id'])
        print(f"Added Subject: {s['name']} (ID: {subject_ids[-1]})")

# 5. Add Staff
staff_data = [
    {"employee_id": "EMP001", "name": "Dr. Alan Turing", "email": "alan@college.edu", "phone": "1234567890", "gender": "male", "designation": "Professor", "qualification": "PhD CS", "department_id": dept_ids[0], "joining_date": "2020-01-15", "status": "active"},
    {"employee_id": "EMP002", "name": "Dr. Ada Lovelace", "email": "ada@college.edu", "phone": "0987654321", "gender": "female", "designation": "Associate Professor", "qualification": "PhD Math", "department_id": dept_ids[1], "joining_date": "2021-06-20", "status": "active"}
]
staff_ids = []
for st in staff_data:
    res = make_request("POST", "/staff/", token, st) # Ensure the trailing slash if required by route, or usually it's just /staff
    if res and res.get("success"):
        staff_ids.append(res['data']['staff_id'])
        print(f"Added Staff: {st['name']} (ID: {staff_ids[-1]})")

# 6. Add Students
# We need a batch and a section first.
import time
current_year = 2024
# Batch
batch_payload = {"college_id": 1, "admission_year": current_year, "label": f"Batch {current_year}"}
res = make_request("POST", "/students/batches", token, batch_payload)
batch_id = None
if res and res.get("success"):
    batch_id = res['data']['batch_id']
    print(f"Added Batch: {batch_payload['label']} (ID: {batch_id})")
else:
    # Try getting existing
    existing = make_request("GET", "/students/batches", token)
    if existing and existing.get('data'):
        batch_id = existing['data'][0]['batch_id']
        print(f"Found existing Batch ID: {batch_id}")

# Section
section_payload = {"batch_id": batch_id, "course_id": course_ids[0], "name": "A", "current_semester": 1}
res = make_request("POST", "/students/sections", token, section_payload)
section_id = None
if res and res.get("success"):
    section_id = res['data']['section_id']
    print(f"Added Section: {section_payload['name']} (ID: {section_id})")
else:
    # Try getting existing
    existing = make_request("GET", "/students/sections", token)
    if existing and existing.get('data'):
        section_id = existing['data'][0]['section_id']
        print(f"Found existing Section ID: {section_id}")

students_data = [
    {"reg_number": "REG001", "roll_number": "R001", "name": "Alice Johnson", "email": "alice@student.col", "phone": "1112223333", "gender": "female", "dob": "2005-05-15", "address": "123 Main St", "blood_group": "O+", "guardian_name": "Bob Johnson", "guardian_phone": "3332221111", "batch_id": batch_id, "section_id": section_id, "course_id": course_ids[0], "admission_type": "regular", "admission_date": f"{current_year}-08-01", "status": "active"},
    {"reg_number": "REG002", "roll_number": "R002", "name": "Bob Smith", "email": "bob@student.col", "phone": "4445556666", "gender": "male", "dob": "2004-11-22", "address": "456 Oak St", "blood_group": "A+", "guardian_name": "Mary Smith", "guardian_phone": "6665554444", "batch_id": batch_id, "section_id": section_id, "course_id": course_ids[0], "admission_type": "regular", "admission_date": f"{current_year}-08-01", "status": "active"},
    {"reg_number": "REG003", "roll_number": "R003", "name": "Charlie Brown", "email": "charlie@student.col", "phone": "7778889999", "gender": "male", "dob": "2005-02-10", "address": "789 Pine St", "blood_group": "B-", "guardian_name": "David Brown", "guardian_phone": "9998887777", "batch_id": batch_id, "section_id": section_id, "course_id": course_ids[0], "admission_type": "regular", "admission_date": f"{current_year}-08-01", "status": "active"},
    {"reg_number": "REG004", "roll_number": "R004", "name": "Diana Ross", "email": "diana@student.col", "phone": "2223334444", "gender": "female", "dob": "2005-09-05", "address": "321 Elm St", "blood_group": "AB+", "guardian_name": "Eva Ross", "guardian_phone": "4443332222", "batch_id": batch_id, "section_id": section_id, "course_id": course_ids[1], "admission_type": "regular", "admission_date": f"{current_year}-08-01", "status": "active"},
    {"reg_number": "REG005", "roll_number": "R005", "name": "Evan Peters", "email": "evan@student.col", "phone": "5556667777", "gender": "male", "dob": "2004-04-18", "address": "654 Cedar St", "blood_group": "O-", "guardian_name": "Frank Peters", "guardian_phone": "7776665555", "batch_id": batch_id, "section_id": section_id, "course_id": course_ids[1], "admission_type": "regular", "admission_date": f"{current_year}-08-01", "status": "active"}
]

for st in students_data:
    res = make_request("POST", "/students", token, st) # Assuming POST /students is the endpoint
    if res and res.get("success"):
        print(f"Added Student: {st['name']} (ID: {res['data'].get('student_id')})")
    else:
        # Check specific error
        print(f"Failed to add student {st['name']}.")

print("Database population script finished.")

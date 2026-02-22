import urllib.request
import json
import sys

# Get token
try:
    data = json.dumps({"username": "superadmin", "password": "Admin@123"}).encode('utf-8')
    req = urllib.request.Request("http://localhost:5000/api/auth/login", data=data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as response:
        res = json.loads(response.read().decode('utf-8'))
        token = res['data']['token']
except Exception as e:
    print("Login failed:", e)
    sys.exit(1)

# Add subject
try:
    subject_data = {
        "course_id": 1,
        "name": "Math 101",
        "code": "M101",
        "semester": 1,
        "credits": 4
    }
    
    data = json.dumps(subject_data).encode('utf-8')
    req = urllib.request.Request("http://localhost:5000/api/courses/subjects", data=data, headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'})
    with urllib.request.urlopen(req) as response:
        print("Status:", response.getcode())
        print(response.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print("HTTP Error:", e.code)
    print("Body:", e.read().decode('utf-8'))
except Exception as e:
    print("Error:", e)

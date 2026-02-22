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

endpoints = [
    "/students/sections",
    "/timetable/periods",
    "/courses/subjects",
    "/staff/",
    "/timetable/rooms",
    "/college/academic-years"
]

for ep in endpoints:
    print(f"\nFetching {ep}...")
    req = urllib.request.Request(f"http://localhost:5000/api{ep}", headers={'Authorization': f'Bearer {token}'})
    try:
        with urllib.request.urlopen(req) as response:
            print("Status:", response.getcode())
    except urllib.error.HTTPError as e:
        print("HTTP Error:", e.code)
        print("Body:", e.read().decode('utf-8'))
    except Exception as e:
        print("Error:", e)

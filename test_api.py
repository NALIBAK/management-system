import requests
import sys

BASE_URL = "http://localhost:5000/api"
DEBUG_URL = "http://localhost:5000/debug/routes"

def write_log(msg):
    with open("api_test_report.txt", "a", encoding="utf-8") as f:
        f.write(msg + "\n")
    print(msg)

def test_routes():
    write_log(f"Fetching routes from {DEBUG_URL}...")
    try:
        resp = requests.get(DEBUG_URL)
        write_log(f"Routes:\n{resp.text}")
    except Exception as e:
        write_log(f"Failed to fetch routes: {e}")

def test_login():
    url = f"{BASE_URL}/auth/login"
    payload = {"username": "superadmin", "password": "Admin@123"}
    try:
        resp = requests.post(url, json=payload)
        if resp.ok:
            token = resp.json()['data']['token']
            write_log("Login Successful")
            return token
        write_log(f"Login Failed: {resp.status_code} {resp.text[:100]}")
    except Exception as e:
        write_log(f"Login Exception: {e}")
    return None

def test_staff(token):
    headers = {"Authorization": f"Bearer {token}"}
    for path in ["/staff", "/staff/"]:
        url = f"{BASE_URL}{path}"
        write_log(f"\nTesting {url}")
        resp = requests.get(url, headers=headers)
        write_log(f"Status: {resp.status_code}")
        if not resp.ok:
            write_log(f"Response: {resp.text[:200]}")

if __name__ == "__main__":
    with open("api_test_report.txt", "w", encoding="utf-8") as f:
        f.write("API Test Report\n")
    test_routes()
    token = test_login()
    if token:
        test_staff(token)

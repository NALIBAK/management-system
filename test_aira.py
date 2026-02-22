import urllib.request
import json

BASE_URL = "http://localhost:5000/api"

# Check Ollama directly
print("=== Checking Ollama ===")
try:
    req = urllib.request.Request("http://localhost:11434/api/tags")
    with urllib.request.urlopen(req, timeout=5) as r:
        models = json.loads(r.read().decode())
        print("Ollama is RUNNING!")
        print("Available models:", [m['name'] for m in models.get('models', [])])
except Exception as e:
    print("Ollama check failed:", e)

# Login
print("\n=== Logging into backend ===")
data = json.dumps({"username": "superadmin", "password": "Admin@123"}).encode('utf-8')
req = urllib.request.Request(f"{BASE_URL}/auth/login", data=data, headers={"Content-Type": "application/json"})
with urllib.request.urlopen(req) as r:
    token = json.loads(r.read().decode())['data']['token']
    print("Logged in OK")

headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}

# Test AIRA with questions
questions = [
    "How many students are there?",
    "List all departments",
    "What is the department summary?",
]
print("\n=== Testing AIRA ===")
for question in questions:
    print(f"\nQ: {question}")
    payload = json.dumps({"message": question}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/aira/chat", data=payload, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            res = json.loads(r.read().decode())
            print(f"A: {res['data']['response'][:200]}")
    except urllib.error.HTTPError as e:
        print("HTTP Error:", e.code, e.read().decode()[:200])
    except Exception as e:
        print("Error:", e)

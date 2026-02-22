import urllib.request
import urllib.error
import sys

req = urllib.request.Request("http://localhost:5000/api/timetable/periods", method="OPTIONS")
req.add_header("Origin", "http://localhost:8000")
req.add_header("Access-Control-Request-Method", "GET")
req.add_header("Access-Control-Request-Headers", "authorization,content-type")

try:
    with urllib.request.urlopen(req) as response:
        print("Status", response.getcode())
        print("Headers", response.getheaders())
except urllib.error.HTTPError as e:
    print("HTTP Error:", e.code)
    print("Headers:", e.headers)
    print("Body:", e.read().decode())

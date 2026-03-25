import urllib.request
import json

base_url = "http://127.0.0.1:8000"
login_url = f"{base_url}/api/auth/login/"
data = json.dumps({"username": "lohi", "password": "Lohi244@"}).encode("utf-8")

req = urllib.request.Request(login_url, data=data, headers={'Content-Type': 'application/json'})

try:
    with urllib.request.urlopen(req) as response:
        print(f"Status: {response.getcode()}")
        print(response.read().decode("utf-8"))
except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code}")
    body = e.read()
    with open("error_response.html", "wb") as f:
        f.write(body)
    print("Error body saved to error_response.html")
except Exception as e:
    print(f"Other Error: {e}")

import json
import urllib.request
import urllib.error

base_url = "http://127.0.0.1:8000"
username = "Lohitha"
password = "password123"

def post_json(url, data, headers={}):
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method='POST')
    req.add_header('Content-Type', 'application/json')
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.getcode(), json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8')

# Login
code, body = post_json(f"{base_url}/api/auth/login/", {"username": username, "password": password})
if code != 200:
    print(f"Login failed: {code}, {body}")
    exit(1)

token = body["access"]
print("Login successful")

# Chat
headers = {"Authorization": f"Bearer {token}"}
code, body = post_json(f"{base_url}/api/chat/send/", {"message": "How are you today?"}, headers=headers)
print(f"Chat status: {code}")
print("Chat response:", body)

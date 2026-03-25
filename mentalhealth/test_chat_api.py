import requests
import json

base_url = "http://127.0.0.1:8000"
username = "Lohitha"
password = "password123"

# 1. Login
login_url = f"{base_url}/api/auth/login/"
data = {"username": username, "password": password}
response = requests.post(login_url, json=data)

if response.status_code != 200:
    print(f"Login failed: {response.status_code}")
    print(response.text)
    exit(1)

token = response.json()["access"]
print("Login successful")

# 2. Chat
chat_url = f"{base_url}/api/chat/send/"
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
chat_data = {"message": "How are you today?"}

try:
    print("Sending chat request...")
    chat_resp = requests.post(chat_url, json=chat_data, headers=headers, timeout=30)
    print(f"Chat status: {chat_resp.status_code}")
    print("Chat response:", chat_resp.json())
except Exception as e:
    print("Chat request error:", e)

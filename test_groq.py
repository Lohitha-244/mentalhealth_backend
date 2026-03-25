import os
from groq import Groq

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY is not set in environment variables")

client = Groq(api_key=api_key)

try:
    resp = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": "hello"}],
        max_tokens=10
    )
    print("SUCCESS:", resp.choices[0].message.content)
except Exception as e:
    print("ERROR:", e)
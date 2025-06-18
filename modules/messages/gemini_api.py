# gemini_api.py
import requests
import os
from dotenv import load_dotenv

load_dotenv()  # Load biến môi trường từ file .env

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent"

def chat_with_gemini(prompt):
    print("[DEBUG] Gọi chat_with_gemini với prompt:", prompt)
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    response = requests.post(
        f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
        headers=headers,
        json=data
    )
    print("Gemini API status:", response.status_code)
    print("Gemini API response:", response.text)
    if response.status_code == 200:
        res = response.json()
        return res['candidates'][0]['content']['parts'][0]['text']
    else:
        return "Xin lỗi, Gemini không thể trả lời lúc này."


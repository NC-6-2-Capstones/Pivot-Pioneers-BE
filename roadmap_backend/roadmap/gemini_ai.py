from google import generativeai as genai
from django.conf import settings
import os

genai.configure(api_key=settings.GEMINI_API_KEY)

def analyze_goal_with_gemini(full_prompt: str) -> str:
    contents = full_prompt

    model = genai.GenerativeModel("gemini-2.0-flash-lite")
    response = model.generate_content(contents)

    return response.text

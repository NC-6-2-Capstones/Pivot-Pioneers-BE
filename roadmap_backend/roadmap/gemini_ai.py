from google import generativeai as genai
from pydantic import BaseModel
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class Assessment(BaseModel):
    q1: str
    q2: str
    q3: str

def analyze_goal_with_gemini(goal: str, assessment: Assessment) -> str:
    contents = f"""
    Goal: {goal}
    Motivation: {assessment.q1}
    Barrier: {assessment.q2}
    Success in 3 months: {assessment.q3}
    """

    model = genai.GenerativeModel("gemini-2.0-flash-lite")
    response = model.generate_content(contents)

    return response.text

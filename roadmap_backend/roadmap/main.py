from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from gemini_ai import analyze_goal_with_gemini  

app = FastAPI()


class AnalyzeRequest(BaseModel):
    prompt: str

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze")
def analyze(request: AnalyzeRequest):
    result = analyze_goal_with_gemini(request.prompt)
    return {"ai_response": result}

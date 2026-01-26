import os
import requests
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

VOICEFLOW_API_KEY = os.getenv("VOICEFLOW_API_KEY")
VOICEFLOW_PROJECT_ID = os.getenv("VOICEFLOW_PROJECT_ID")
BASE_URL = "https://general-runtime.voiceflow.com"

app = FastAPI()

class UserMessage(BaseModel):
    user_id: str
    message: str

def ask_voiceflow(user_id: str, message: str):
    url = f"{BASE_URL}/state/{VOICEFLOW_PROJECT_ID}/user/{user_id}/interact"
    headers = {
        "Authorization": VOICEFLOW_API_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "type": "text",
        "payload": message,
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()

@app.post("/ask")
def ask(data: dict):
    return {
        "response": {
            "type": "text",
            "payload": "Привет, я работаю и это новый код 🚀"
        }
    }


@app.get("/healthz")
def healthz():
    return {"status": "ok"}

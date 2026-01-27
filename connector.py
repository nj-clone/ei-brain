import os
import requests
from fastapi import FastAPI
from pydantic import BaseModel

VOICEFLOW_API_KEY = os.getenv("VOICEFLOW_API_KEY")
VOICEFLOW_PROJECT_ID = os.getenv("VOICEFLOW_PROJECT_ID")

app = FastAPI()

class UserMessage(BaseModel):
    message: str

@app.post("/ask")
def ask(data: UserMessage):
    url = f"https://general-runtime.voiceflow.com/state/{VOICEFLOW_PROJECT_ID}/user/flutter_user/interact"

    headers = {
        "Authorization": VOICEFLOW_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "request": {
            "type": "text",
            "payload": {
                "text": data.message
            }
        }
    }

    r = requests.post(url, headers=headers, json=payload)
    r.raise_for_status()

    traces = r.json()

    # временно — возвращаем СЫРОЙ ответ Voiceflow
    return traces

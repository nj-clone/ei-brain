import os
import requests
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

VOICEFLOW_API_KEY = os.getenv("VOICEFLOW_API_KEY")
VOICEFLOW_VERSION_ID = os.getenv("VOICEFLOW_VERSION_ID")
BASE_URL = "https://general-runtime.voiceflow.com"

app = FastAPI()


class UserMessage(BaseModel):
    user_id: str
    message: str


def ask_voiceflow(user_id: str, message: str) -> str:
    url = f"{BASE_URL}/state/{VOICEFLOW_VERSION_ID}/user/{user_id}/interact"

    headers = {
        "Authorization": VOICEFLOW_API_KEY,
        "Content-Type": "application/json",
    }

    # 🔴 ВАЖНО: Voiceflow принимает ТОЛЬКО text
    payload = {
        "request": {
            "type": "text",
            "payload": {
                "text": message
            }
        }
    }

    r = requests.post(url, headers=headers, json=payload)
    r.raise_for_status()

    data = r.json()

    # Voiceflow ВСЕГДА возвращает массив трасс
    for item in data:
        if item.get("type") == "text":
            text = item.get("payload", {}).get("text")
            if isinstance(text, str) and text.strip():
                return text

    return ""


@app.post("/ask")
def ask(data: UserMessage):
    answer = ask_voiceflow(data.user_id, data.message)
    return {
        "response": {
            "text": answer
        }
    }

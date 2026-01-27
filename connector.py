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

def extract_text(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in ("text", "message") and isinstance(v, str):
                return v
            result = extract_text(v)
            if result:
                return result
    elif isinstance(obj, list):
        for item in obj:
            result = extract_text(item)
            if result:
                return result
    return ""

answer = extract_text(data)
return answer


@app.post("/ask")
def ask(data: UserMessage):
    answer = ask_voiceflow(data.user_id, data.message)
    return {
        "response": {
            "text": answer
        }
    }

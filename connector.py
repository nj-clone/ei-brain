import os
import requests
from fastapi import FastAPI, Body

app = FastAPI()

VOICEFLOW_API_KEY = os.getenv("VOICEFLOW_API_KEY")
VOICEFLOW_PROJECT_ID = os.getenv("VOICEFLOW_PROJECT_ID")  # именно project_id

@app.post("/ask")
def ask(message: str = Body(..., embed=True)):
    url = "https://general-runtime.voiceflow.com/interact"

    payload = {
        "request": {
            "type": "text",
            "payload": {
                "text": message
            }
        }
    }

    headers = {
        "Authorization": f"Bearer {VOICEFLOW_API_KEY}",
        "Content-Type": "application/json"
    }

    params = {
        "projectID": VOICEFLOW_PROJECT_ID,
        "userID": "flutterflow-user"
    }

    response = requests.post(
        url,
        json=payload,
        headers=headers,
        params=params,
        timeout=30
    )

    return response.json()

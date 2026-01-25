import os
import requests
from dotenv import load_dotenv

# Загружаем .env
load_dotenv()

VOICEFLOW_API_KEY = os.getenv("VOICEFLOW_API_KEY")
VOICEFLOW_PROJECT_ID = os.getenv("VOICEFLOW_PROJECT_ID")

BASE_URL = "https://general-runtime.voiceflow.com"

def ask_voiceflow(user_id: str, message: str):
    url = f"{BASE_URL}/state/{VOICEFLOW_PROJECT_ID}/user/{user_id}/interact"

    headers = {
        "Authorization": VOICEFLOW_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "type": "text",
        "payload": message
    }

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()

    return response.json()


if __name__ == "__main__":
    print("🧠 Expert Nazira Family online")
    while True:
        text = input("Ты: ")
        if text.lower() in ["выход", "exit", "quit"]:
            break

        result = ask_voiceflow("nazira_local_test", text)

        for item in result:
            if item.get("type") == "text":
                print("Мозг:", item["payload"]["message"])


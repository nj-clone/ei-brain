def ask_voiceflow(user_id: str, message: str):
    url = f"{BASE_URL}/state/{VOICEFLOW_PROJECT_ID}/user/{user_id}/interact"

    headers = {
        "Authorization": VOICEFLOW_API_KEY,
        "Content-Type": "application/json",
    }

    payload = {
        "type": "text",
        "payload": message
    }

    r = requests.post(url, headers=headers, json=payload)
    r.raise_for_status()

    data = r.json()

    # вытаскиваем первый текстовый ответ
    text_response = ""

    for item in data:
        if item.get("type") == "text":
            text_response = item.get("payload", "")
            break

    return {
        "response": {
            "text": text_response
        }
    }

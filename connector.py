from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os
import uuid
from fastapi.responses import RedirectResponse
app = FastAPI()

VOICEFLOW_API_KEY = os.getenv("VOICEFLOW_API_KEY")
VOICEFLOW_PROJECT_ID = os.getenv("VOICEFLOW_PROJECT_ID")

class UserMessage(BaseModel):
    message: str
    user_id: str | None = None

@app.post("/ask")
def ask_voiceflow(data: UserMessage):
    user_id = data.user_id or str(uuid.uuid4())

    url = f"https://general-runtime.voiceflow.com/state/user/{user_id}/interact"

    headers = {
        "Authorization": VOICEFLOW_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
    "request": {
        "type": "text",
        "payload": data.message
    },
    "config": {
        "tts": False,
        "stripSSML": True
    }
}

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        params={"projectID": VOICEFLOW_PROJECT_ID}
    )

    if response.status_code != 200:
        return {"error": response.text}

    traces = response.json()

    texts = []
    for trace in traces:
        if trace.get("type") == "text":
            texts.append(trace["payload"]["message"])

    return {
        "text": "\n".join(texts)
    }

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.options("/ask")
async def options_ask():
    return {}


from fastapi import Request
import stripe

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

from fastapi.responses import JSONResponse

@app.get("/create-checkout-session")
async def create_checkout_session(request: Request):

    email = request.query_params.get("email")
    uid = request.query_params.get("uid")

    session = stripe.checkout.Session.create(
    payment_method_types=["card"],
    mode="payment",
    customer_email=email,
    metadata={
        "user_id": uid
    },
    line_items=[{
        "price_data": {
            "currency": "usd",
            "product_data": {
                "name": "Zodiac Wisdom",
            },
            "unit_amount": 999,
        },
        "quantity": 1,
    }],
    success_url="https://seyidkona.flutterflow.app/njCORE",
    cancel_url="https://seyidkona.flutterflow.app/payment",
)

    return RedirectResponse(session.url)

# ================= FIREBASE + STRIPE TIME LOGIC =================

import os
import stripe
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timedelta
from fastapi import Request

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Инициализация Firebase
if not firebase_admin._apps:
    import json
    firebase_json = os.getenv("FIREBASE_KEY_JSON")
    cred = credentials.Certificate(json.loads(firebase_json))
    firebase_admin.initialize_app(cred)

db = firestore.client()

@app.post("/stripe-webhook")
async def stripe_webhook(request: Request):

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            os.getenv("STRIPE_WEBHOOK_SECRET")
        )
    except Exception as e:
        return {"error": str(e)}

    # ВАЖНО: ВСЁ НИЖЕ ВНУТРИ ФУНКЦИИ
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

    metadata = session.get("metadata", {})
    uid = metadata.get("user_id")

    if not uid:
        print("No user_id in metadata")
    return {"status": "no user id"}

    user_ref = db.collection("users").document(uid)

    user_ref.update({
        "minutesRemaining": 10,
        "hasAccess": True,
        "expiresAt": datetime.utcnow() + timedelta(minutes=10)
    })

    print(f"10 minutes granted to UID: {uid}")
    return {"status": "success"}

    return {"status": "ignored"}
    
import os
import uuid
import requests
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException

app = FastAPI()


@app.post("/create-forte-order")
async def create_forte_order(data: dict):

    uid = data.get("uid")
    plan = data.get("plan")
    print ("PLAN RECEIVED:", plan)

    if not uid or not plan:
        raise HTTPException(status_code=400, detail="Missing uid or plan")

    plan = plan.strip().lower()

    print ("PLAN AFTER STRIP:", plan)
    
    if plan == "hour":
        amount = "9990.00"
        expires_at = datetime.utcnow() + timedelta(hours=1)

    elif plan == "day":
        amount = "29990.00"
        expires_at = datetime.utcnow() + timedelta(days=1)

    elif plan == "month":
        amount = "79990.00"
        expires_at = datetime.utcnow() + timedelta(days=30)

    else:
        raise HTTPException(status_code=400, detail="Invalid plan")

    forte_url = os.getenv("FORTE_API_URL")
    username = os.getenv("FORTE_USERNAME")
    password = os.getenv("FORTE_PASSWORD")

    payload = {
        "order": {
            "typeRid": "Order_RID",
            "language": "en",
            "amount": amount,
            "currency": "KZT",
            "hppRedirectUrl": "https://nj-web.flutterflow.app//paywall",
            "description": f"Subscription {plan}",
            "title": "Subscription"
        }
    }

    try:
        response = requests.post(
            f"{forte_url}/order",
            json=payload,
            auth=(username, password),
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=str(e))

    forte_response = response.json()

    return {
        "orderId": forte_response["order"]["id"],
        "hppUrl": forte_response["order"]["hppUrl"],
        "password": forte_response["order"]["password"],
        "plan": plan,
        "expiresAt": expires_at.isoformat()
    }

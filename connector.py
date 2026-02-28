from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import os
import uuid
import json
import requests
import stripe
import firebase_admin

from firebase_admin import credentials, firestore
from datetime import datetime, timedelta


app = FastAPI()

# ================= CORS =================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= ENV VARIABLES =================

VOICEFLOW_API_KEY = os.getenv("VOICEFLOW_API_KEY")
VOICEFLOW_PROJECT_ID = os.getenv("VOICEFLOW_PROJECT_ID")

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

FORTE_API_URL = os.getenv("FORTE_API_URL")
FORTE_USERNAME = os.getenv("FORTE_USERNAME")
FORTE_PASSWORD = os.getenv("FORTE_PASSWORD")

stripe.api_key = STRIPE_SECRET_KEY

# ================= FIREBASE INIT =================

if not firebase_admin._apps:
    firebase_json = os.getenv("FIREBASE_KEY_JSON")
    cred = credentials.Certificate(json.loads(firebase_json))
    firebase_admin.initialize_app(cred)

db = firestore.client()

# ================= VOICEFLOW =================

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

    texts = [
        trace["payload"]["message"]
        for trace in traces
        if trace.get("type") == "text"
    ]

    return {"text": "\n".join(texts)}


# ================= STRIPE CHECKOUT =================

@app.get("/create-checkout-session")
async def create_checkout_session(request: Request):

    email = request.query_params.get("email")
    uid = request.query_params.get("uid")

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",
        customer_email=email,
        metadata={"user_id": uid},
        line_items=[{
            "price_data": {
                "currency": "usd",
                "product_data": {"name": "Zodiac Wisdom"},
                "unit_amount": 999,
            },
            "quantity": 1,
        }],
        success_url="https://seyidkona.flutterflow.app/njCORE",
        cancel_url="https://seyidkona.flutterflow.app/payment",
    )

    return RedirectResponse(session.url)


# ================= STRIPE WEBHOOK =================

@app.post("/stripe-webhook")
async def stripe_webhook(request: Request):

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            STRIPE_WEBHOOK_SECRET
        )
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        metadata = session.get("metadata", {})
        uid = metadata.get("user_id")

        if not uid:
            return {"status": "no user id"}

        user_ref = db.collection("users").document(uid)

        expires_at = datetime.utcnow() + timedelta(minutes=10)

        user_ref.update({
            "minutesRemaining": 10,
            "hasAccess": True,
            "expiresAt": expires_at
        })

        return {"status": "success"}

    return {"status": "ignored"}


from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import os
import uuid
import json
import requests
import stripe
import firebase_admin

from firebase_admin import credentials, firestore
from datetime import datetime, timedelta


app = FastAPI()

# ================= CORS =================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= ENV VARIABLES =================

VOICEFLOW_API_KEY = os.getenv("VOICEFLOW_API_KEY")
VOICEFLOW_PROJECT_ID = os.getenv("VOICEFLOW_PROJECT_ID")

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

FORTE_API_URL = os.getenv("FORTE_API_URL")
FORTE_USERNAME = os.getenv("FORTE_USERNAME")
FORTE_PASSWORD = os.getenv("FORTE_PASSWORD")

stripe.api_key = STRIPE_SECRET_KEY

# ================= FIREBASE INIT =================

if not firebase_admin._apps:
    firebase_json = os.getenv("FIREBASE_KEY_JSON")
    cred = credentials.Certificate(json.loads(firebase_json))
    firebase_admin.initialize_app(cred)

db = firestore.client()

# ================= VOICEFLOW =================

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

    texts = [
        trace["payload"]["message"]
        for trace in traces
        if trace.get("type") == "text"
    ]

    return {"text": "\n".join(texts)}


# ================= STRIPE CHECKOUT =================

@app.get("/create-checkout-session")
async def create_checkout_session(request: Request):

    email = request.query_params.get("email")
    uid = request.query_params.get("uid")

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",
        customer_email=email,
        metadata={"user_id": uid},
        line_items=[{
            "price_data": {
                "currency": "usd",
                "product_data": {"name": "Zodiac Wisdom"},
                "unit_amount": 999,
            },
            "quantity": 1,
        }],
        success_url="https://seyidkona.flutterflow.app/njCORE",
        cancel_url="https://seyidkona.flutterflow.app/payment",
    )

    return RedirectResponse(session.url)


# ================= STRIPE WEBHOOK =================

@app.post("/stripe-webhook")
async def stripe_webhook(request: Request):

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            STRIPE_WEBHOOK_SECRET
        )
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        metadata = session.get("metadata", {})
        uid = metadata.get("user_id")

        if not uid:
            return {"status": "no user id"}

        user_ref = db.collection("users").document(uid)

        expires_at = datetime.utcnow() + timedelta(minutes=10)

        user_ref.update({
            "minutesRemaining": 10,
            "hasAccess": True,
            "expiresAt": expires_at
        })

        return {"status": "success"}

    return {"status": "ignored"}


# ================= FORTE CREATE ORDER =================

@app.get("/create-forte-order")
async def create_forte_order(uid: str, plan: str):

    forte_url = os.getenv("FORTE_API_URL")
    username = os.getenv("FORTE_USERNAME")
    password = os.getenv("FORTE_PASSWORD")

    if not forte_url or not username or not password:
        raise HTTPException(status_code=500, detail="Forte credentials not configured")

    plan = plan.strip().lower()

    if plan == "hour":
        amount = "9990.00"

    elif plan == "day":
        amount = "29990.00"

    elif plan == "month":
        amount = "89990.00"

    else:
        raise HTTPException(status_code=400, detail="Invalid plan")

    payload = {
        "order": {
            "typeRid": "Order_RID",
            "language": "en",
            "amount": amount,
            "currency": "KZT",
            "hppRedirectUrl": "https://nj-web.flutterflow.app/paywall",
            "description": f"Subscription {plan}",
            "title": "Subscription"
        }
    }

    response = requests.post(
        f"{forte_url}/order",
        json=payload,
        auth=(FORTE_USERNAME, FORTE_PASSWORD),
        headers={"Content-Type": "application/json"}
    )

    response.raise_for_status()

    forte_response = response.json()

    order_id = forte_response["order"]["id"]
    password = forte_response["order"]["password"]
    hpp_url = forte_response["order"]["hppUrl"]

    pay_url = f"{hpp_url}?id={order_id}&password={password}"

    print("HPP URL:", hpp_url)
    print("PAY URL:", pay_url)

    return RedirectResponse(pay_url)

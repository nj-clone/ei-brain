from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class UserMessage(BaseModel):
    message: str

@app.post("/ask")
def ask(data: UserMessage):
    return {
        "response": {
            "text": f"Привет! Ты написала: {data.message}"
        }
    }

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

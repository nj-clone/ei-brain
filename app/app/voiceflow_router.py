from fastapi import APIRouter

router = APIRouter()

@router.get("/voiceflow-test")
def test():
    return {"status": "voiceflow router ok"}

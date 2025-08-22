from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, ConfigDict
from datetime import datetime
import uvicorn
import os
from dotenv import load_dotenv

from llm_prod import process_request as process_prod_request
from llm_dev import process_request as process_dev_request    

# --- Import services ---
from services.logger import log_content, log_html, log_raw_req
from services.fetcher import fetch_html
# from llm import process_request

app = FastAPI()
security = HTTPBearer()

# Load environment variables
load_dotenv()
SECRET_TOKEN = os.getenv("BEARER_TOKEN")

class RunRequest(BaseModel):
    model_config = ConfigDict(extra='allow')
    questions: list[str]

# ✅ Middleware for logging raw requests
@app.middleware("http")
async def log_raw_request_middleware(request: Request, call_next):
    try:
        body = await request.body()
        log_raw_req(body.decode("utf-8"))
    except Exception as e:
        print(e)
        print(f"[WARN] Could not log raw request: {e}")
    response = await call_next(request)
    return response

# ✅ Bearer token verification
async def verify_token(token: str = "dummy_token"):
    """
    A placeholder dependency to verify a token.
    In a real app, you would implement your authentication logic here.
    """
    # For example: if token != "your-secret-token": raise HTTPException(...)
    return token

@app.post("/hackrx/prod")
async def run_prod(req: RunRequest, token: str = Depends(verify_token)):
    timestamp = datetime.utcnow().isoformat()
    # url = req.url
    # questions = req.questions

    try:
        ai_response = await process_prod_request(req.dict())
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Agent processing failed: {e}")

    response_data = {
        "answers": ai_response.get("answers", ["Agent did not provide a valid answer."]),
    }

    return response_data

@app.post("/hackrx/dev")
async def run_prod(req: RunRequest, token: str = Depends(verify_token)):
    timestamp = datetime.utcnow().isoformat()
    # url = req.url
    # questions = req.questions

    try:
        ai_response = await process_dev_request(req.dict())
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Agent processing failed: {e}")

    response_data = {
        "answers": ai_response.get("answers", ["Agent did not provide a valid answer."]),
    }

    return response_data

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

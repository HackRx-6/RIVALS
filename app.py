from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from datetime import datetime
import uvicorn
import os
from dotenv import load_dotenv

# --- Import services ---
from services.logger import log_content, log_html, log_raw_req
from services.fetcher import fetch_html
from llm import process_request

app = FastAPI()
security = HTTPBearer()

# Load environment variables
load_dotenv()
SECRET_TOKEN = os.getenv("BEARER_TOKEN")

class RunRequest(BaseModel):
    url: str
    questions: list[str]

# ✅ Middleware for logging raw requests
@app.middleware("http")
async def log_raw_request_middleware(request: Request, call_next):
    try:
        body = await request.body()
        log_raw_req(body.decode("utf-8"))
    except Exception as e:
        print(f"[WARN] Could not log raw request: {e}")
    response = await call_next(request)
    return response

# ✅ Bearer token verification
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not SECRET_TOKEN or credentials.credentials != SECRET_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid or missing token")
    return credentials.credentials

@app.post("/hackrx/dev")
async def run_dev(req: RunRequest, token: str = Depends(verify_token)):
    timestamp = datetime.utcnow().isoformat()
    url = req.url
    questions = req.questions

    # Fetch HTML
    html_content = await fetch_html(url)

    # Placeholder answers
    response_data = {
        "answers": [f"Answer placeholder for: {q}" for q in questions],
    }

    # Logs
    log_content(req.dict(), url, questions, timestamp, response_data)
    log_html(req.dict(), url, html_content)

    return response_data

@app.post("/hackrx/prod")
async def run_prod(req: RunRequest, token: str = Depends(verify_token)):
    timestamp = datetime.utcnow().isoformat()
    url = req.url
    questions = req.questions

    try:
        ai_response = process_request(req.dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent processing failed: {e}")

    response_data = {
        "answers": ai_response.get("answers", ["Agent did not provide a valid answer."]),
    }

    return response_data

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

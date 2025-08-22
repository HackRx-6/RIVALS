from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from datetime import datetime
import uvicorn

# Import helpers from services/
from services.fetcher import fetch_html
from services.logger import log_content, log_html
from dotenv import load_dotenv
import os

app = FastAPI()
security = HTTPBearer()

# Load environment variables
load_dotenv()
SECRET_TOKEN = os.getenv("BEARER_TOKEN")

class RunRequest(BaseModel):
    url: str
    questions: list[str]

# ✅ Bearer token verification
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    print("[DEBUG] Verifying bearer token...")
    if credentials.credentials != SECRET_TOKEN:
        print("[DEBUG] Invalid token received!")
        raise HTTPException(status_code=403, detail="Invalid or missing token")
    print("[DEBUG] Bearer token verified")
    return credentials.credentials

@app.post("/hackrx/dev")
async def run(req: RunRequest, token: str = Depends(verify_token)):
    print(f"[DEBUG] Received request: {req.dict()}")

    timestamp = datetime.utcnow().isoformat()
    url = req.url
    questions = req.questions

    # 🔹 Fetch HTML
    print(f"[DEBUG] Fetching HTML from {url}")
    html_content = await fetch_html(url)
    print(f"[DEBUG] Successfully fetched HTML ({len(html_content)} chars)")

    # 🔹 Simulated answers
    response_data = {
        "url": url,
        "questions": questions,
        "answers": [f"Answer placeholder for: {q}" for q in questions],
    }
    print(f"[DEBUG] Prepared response: {response_data}")

    # 🔹 Log requests & responses
    log_content(req.dict(), url, questions, timestamp, response_data)
    log_html(req.dict(), url, html_content)
    print("[DEBUG] Logs written successfully")

    return response_data

@app.post("/hackrx/prod")
async def run(req: RunRequest, token: str = Depends(verify_token)):
    print(f"[DEBUG] Received request: {req.dict()}")

    timestamp = datetime.utcnow().isoformat()
    url = req.url
    questions = req.questions

    # 🔹 Fetch HTML
    print(f"[DEBUG] Fetching HTML from {url}")
    html_content = await fetch_html(url)
    print(f"[DEBUG] Successfully fetched HTML ({len(html_content)} chars)")

    # 🔹 Simulated answers
    response_data = {
        "url": url,
        "questions": questions,
        "answers": [f"Answer placeholder for: {q}" for q in questions],
    }
    print(f"[DEBUG] Prepared response: {response_data}")

    # 🔹 Log requests & responses
    log_content(req.dict(), url, questions, timestamp, response_data)
    log_html(req.dict(), url, html_content)
    print("[DEBUG] Logs written successfully")

    return response_data

if __name__ == "__main__":
    print("[DEBUG] Starting server at http://127.0.0.1:8000 ...")
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from datetime import datetime
import uvicorn
import os
from dotenv import load_dotenv

# --- Import the OpenAI orchestrator function ---
# This assumes your main_openai_caller.py file is in the same directory or accessible.
from llm import process_request

# --- Import your existing services (optional, as agent handles fetching) ---
# from services.fetcher import fetch_html
from services.logger import log_content, log_html

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
    if not SECRET_TOKEN or credentials.credentials != SECRET_TOKEN:
        print("[DEBUG] Invalid or missing token!")
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
        # "url": url,
        # "questions": questions,
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

    # 🔹 Call the OpenAI agent to process the request and get answers
    # The agent will handle all browser interactions (fetching, clicking, etc.)
    print("[DEBUG] Handing request to OpenAI agent...")
    try:
        # The req.dict() format matches what process_request expects
        ai_response = process_request(req.dict())
        print(f"[DEBUG] Received final response from agent: {ai_response}")
    except Exception as e:
        print(f"[ERROR] An error occurred during agent processing: {e}")
        raise HTTPException(status_code=500, detail=f"Agent processing failed: {e}")

    # 🔹 Prepare the final response data using the agent's answers
    response_data = {
        # "url": url,
        # "questions": questions,
        # Use .get() for safety in case the agent's response is malformed
        "answers": ai_response.get("answers", ["Agent did not provide a valid answer."]),
    }
    print(f"[DEBUG] Prepared final response: {response_data}")

    # 🔹 Log requests & responses (optional)
    # Note: The agent fetches the HTML internally, so a separate fetch might be redundant.
    # You can log the final HTML state from the agent if needed.
    # For now, we log the final answer.
    # log_content(req.dict(), url, questions, timestamp, response_data)
    # log_html(req.dict(), url, "HTML content fetched by agent if available")
    print("[DEBUG] Task complete.")

    return response_data

if __name__ == "__main__":
    print("[DEBUG] Starting FastAPI server at http://127.0.0.1:8000 ...")
    # Ensure you have a .env file with OPENAI_API_KEY and BEARER_TOKEN
    uvicorn.run(app, host="127.0.0.1", port=8000)

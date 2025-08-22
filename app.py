from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from datetime import datetime
import uvicorn
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
from client import get_client, MODEL
# --- Utils ---
from utils.read_subscription_key import read_subscription_key
from utils.write_subscription_key import write_subscription_key
from utils.beautify import beautify_text

# --- LLM handlers ---
from llm_prod import process_request as process_prod_request
from llm_dev import process_request as process_dev_request    

# --- Logging services ---
from services.logger import log_raw_req

app = FastAPI()
security = HTTPBearer()

# Load environment variables
load_dotenv()
SECRET_TOKEN = os.getenv("BEARER_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


# -----------------------------
# Singleton pattern for AsyncOpenAI client
# -----------------------------




# -----------------------------
# Request models
# -----------------------------
class RunRequest(BaseModel):
    url: str
    questions: list[str]


# -----------------------------
# Middleware for logging raw requests
# -----------------------------
@app.middleware("http")
async def log_raw_request_middleware(request: Request, call_next):
    try:
        body = await request.body()
        log_raw_req(body.decode("utf-8"))
    except Exception as e:
        print(f"[WARN] Could not log raw request: {e}")
    response = await call_next(request)
    return response


# -----------------------------
# Placeholder token verification
# -----------------------------
async def verify_token(token: str = "dummy_token"):
    return token


# -----------------------------
# /hackrx/prod route
# -----------------------------
@app.post("/hackrx/prod")
async def run_prod(req: RunRequest, token: str = Depends(verify_token)):
    # Update keys dynamically
    write_subscription_key("YOUR_PLACEHOLDER_API_KEY".strip(),"api_key.txt")
    write_subscription_key("sk-spgw-api01-f687cb7fbb4886346b2f59c0d39c8c18".strip(),"subscription_key.txt")
    write_subscription_key("https://register.hackrx.in/llm/openai".strip(),"base_url.txt")

    client = get_client()  # fresh client with updated keys
    print(client.api_key)
    print(client.base_url)
    print(client.default_headers)
    try:
        ai_response = await process_prod_request(req.dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent processing failed: {e}")

    answers = [beautify_text(a) for a in ai_response.get("answers", ["Agent did not provide a valid answer."])]

    return {"answers": answers}


# -----------------------------
# /hackrx/dev route
# -----------------------------
@app.post("/hackrx/dev")
async def run_dev(req: RunRequest, token: str = Depends(verify_token)):
    # Write keys
    write_subscription_key(OPENAI_API_KEY.strip(), "api_key.txt")
    write_subscription_key("", "subscription_key.txt")
    write_subscription_key("", "base_url.txt")

    client = get_client()  # always gets fresh client with correct keys

    print("DEBUG CLIENT HEADERS:", client.default_headers)
    print("DEBUG CLIENT API KEY:", client.api_key)
    print("DEBUG CLIENT BASE URL:", client.base_url)

    try:
        ai_response = await process_dev_request(req.dict())
    except Exception as e:
        import traceback
        traceback.print_exc()  # full stack trace
        raise HTTPException(status_code=500, detail=str(e))

    answers = [beautify_text(a) for a in ai_response.get("answers", ["Agent did not provide a valid answer."])]
    return {"answers": answers}


# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

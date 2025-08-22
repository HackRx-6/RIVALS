import json
import os
from datetime import datetime

LOGS_DIR = "logs"
CONTENT_LOG = os.path.join(LOGS_DIR, "logs_content.json")
HTML_LOG = os.path.join(LOGS_DIR, "logs_html.json")
RAW_REQ_LOG = os.path.join(LOGS_DIR, "logs_raw_req.json")

os.makedirs(LOGS_DIR, exist_ok=True)

def _append_to_json_file(file_path, entry):
    data = []
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
        except Exception:
            data = []
    data.append(entry)
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)

def log_content(req_data, url, questions, timestamp, response_data):
    entry = {
        "timestamp": timestamp,
        "url": url,
        "questions": questions,
        "request": req_data,
        "response": response_data,
    }
    _append_to_json_file(CONTENT_LOG, entry)

def log_html(req_data, url, html_content):
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "url": url,
        "request": req_data,
        "html_content": html_content[:1000],  # truncate for readability
    }
    _append_to_json_file(HTML_LOG, entry)

def log_raw_req(raw_body: str):
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "raw_body": raw_body,
    }
    _append_to_json_file(RAW_REQ_LOG, entry)

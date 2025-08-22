import os
import json

LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
LOG_CONTENT_PATH = os.path.join(LOGS_DIR, "logs_content.json")
LOG_HTML_PATH = os.path.join(LOGS_DIR, "logs_html.json")

def log_content(request, url, questions, timestamp, response):
    log_entry = {
        "request": request,
        "url": url,
        "questions": questions,
        "timestamp": timestamp,
        "response": response,
    }
    print(f"[DEBUG] Logging content to {LOG_CONTENT_PATH}")
    _append_to_file(LOG_CONTENT_PATH, log_entry)

def log_html(request, url, html_content):
    log_entry = {
        "request": request,
        "url": url,
        "html": html_content,
    }
    print(f"[DEBUG] Logging HTML to {LOG_HTML_PATH}")
    _append_to_file(LOG_HTML_PATH, log_entry)

def _append_to_file(file_path, log_entry):
    try:
        if os.path.exists(file_path):
            with open(file_path, "r+", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = []
                data.append(log_entry)
                f.seek(0)
                json.dump(data, f, indent=4)
        else:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump([log_entry], f, indent=4)
        print(f"[DEBUG] Log successfully written to {file_path}")
    except Exception as e:
        print(f"[ERROR] Failed to log to {file_path}: {e}")

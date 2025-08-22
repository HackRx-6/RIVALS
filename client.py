# client.py
from openai import AsyncOpenAI
from utils.read_subscription_key import read_subscription_key

MODEL = "gpt-4.1"

_client_instance = None

def get_client():
    global _client_instance
    
    api_key = read_subscription_key("api_key.txt").strip() or None
    subscription_key = read_subscription_key("subscription_key.txt").strip() or None
    base_url = read_subscription_key("base_url.txt").strip() or None

    default_headers = {}
    if subscription_key:
        default_headers["x-subscription-key"] = subscription_key

    _client_instance = AsyncOpenAI(
        api_key=api_key,
        base_url=base_url,
        default_headers=default_headers
    )
    return _client_instance

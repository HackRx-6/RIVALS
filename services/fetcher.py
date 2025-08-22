import httpx

async def fetch_html(url: str) -> str:
    print(f"[DEBUG] Sending GET request to {url}")
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        print("[DEBUG] Received response from URL")
        return response.text

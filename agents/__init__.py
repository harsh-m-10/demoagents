import os
import httpx
from dotenv import load_dotenv

# Load environment variables from .env (if present)
load_dotenv()

_API_URL = "https://api.mistral.ai/v1/chat/completions"

def get_llm_response(prompt: str, model: str = "mistral-small-latest") -> str:
    """Send a prompt to Mistral and return the response text.
    Uses a direct HTTP call — no SDK required.
    """
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        raise RuntimeError("MISTRAL_API_KEY not set in .env file")

    resp = httpx.post(
        _API_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]

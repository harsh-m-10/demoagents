"""Quick debug: test the Mistral API directly."""
import os
from dotenv import load_dotenv
import httpx

load_dotenv()

api_key = os.getenv("MISTRAL_API_KEY")
print(f"API Key loaded: {'YES (' + api_key[:10] + '...)' if api_key else 'NO'}")

resp = httpx.post(
    "https://api.mistral.ai/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    },
    json={
        "model": "mistral-small-latest",
        "messages": [{"role": "user", "content": "Say hello in one sentence."}],
    },
    timeout=30,
)
print(f"Status: {resp.status_code}")
data = resp.json()
if resp.status_code == 200:
    print(f"Response: {data['choices'][0]['message']['content']}")
else:
    print(f"Error: {data}")

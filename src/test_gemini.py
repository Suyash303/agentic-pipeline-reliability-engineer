import os
from google import genai
from google.genai import types

print("Connecting to Gemini...", flush=True)

client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"],
    http_options=types.HttpOptions(
        timeout=30000,
        retry_options=types.HttpRetryOptions(attempts=1)
    )
)

try:
    print("Sending request...", flush=True)

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents="Say hello in one sentence."
    )

    print("Gemini Response:")
    print(response.text)

except Exception as e:
    print("Error type:", type(e).__name__)
    print("Error details:", str(e))

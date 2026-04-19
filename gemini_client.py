from google import genai
from google.genai import types
from config import GEMINI_API_KEY, SYSTEM_PROMPT

client = genai.Client(api_key=GEMINI_API_KEY)

def get_gemini_response(user_message: str) -> str:
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=user_message,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
        ),
    )
    return response.text

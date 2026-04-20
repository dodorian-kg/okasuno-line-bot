import logging
from google import genai
from google.genai import types
from config import GEMINI_API_KEY, SYSTEM_PROMPT
from supabase_client import get_all_faqs, format_faqs_for_prompt

logger = logging.getLogger(__name__)

client = genai.Client(api_key=GEMINI_API_KEY)


def _build_system_instruction() -> str:
    try:
        faq_block = format_faqs_for_prompt(get_all_faqs())
    except Exception as e:
        logger.warning(f"FAQ取得失敗、空プロンプトで続行: {e}")
        faq_block = "(店舗情報が取得できませんでした)"
    return f"{SYSTEM_PROMPT}\n\n## 店舗情報(最新)\n{faq_block}"


def get_gemini_response(user_message: str) -> str:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=user_message,
        config=types.GenerateContentConfig(
            system_instruction=_build_system_instruction(),
        ),
    )
    return response.text

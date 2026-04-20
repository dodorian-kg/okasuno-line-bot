from dotenv import load_dotenv
import os

load_dotenv()

LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

ADMIN_LINE_TARGET_ID = os.getenv("ADMIN_LINE_TARGET_ID")

HANDOFF_PHRASE = "スタッフにお繋ぎしましょうか？"

SYSTEM_PROMPT = (
    "あなたはスノーボードグッズレンタルショップ「おかスノ」のカスタマーサポートBotです。"
    "お客様のレンタル料金・予約・営業時間などの問い合わせに、丁寧かつ簡潔に日本語で答えてください。"
    "回答は必ず下記「店舗情報(最新)」に含まれる事実のみを根拠としてください。"
    "そこに書かれていない内容は推測せず、その場合は最後に必ず"
    f"「{HANDOFF_PHRASE}」"
    "と問いかけてください（この定型文は FAQ の本文には書かないでください。"
    "ユーザーが「はい」「お願いします」等で承認した場合にスタッフへの通知がトリガーされます）。"
)

for _name, _val in [
    ("LINE_CHANNEL_SECRET", LINE_CHANNEL_SECRET),
    ("LINE_CHANNEL_ACCESS_TOKEN", LINE_CHANNEL_ACCESS_TOKEN),
    ("GEMINI_API_KEY", GEMINI_API_KEY),
    ("SUPABASE_URL", SUPABASE_URL),
    ("SUPABASE_KEY", SUPABASE_KEY),
]:
    if not _val:
        raise ValueError(f"環境変数 {_name} が設定されていません。.envを確認してください。")

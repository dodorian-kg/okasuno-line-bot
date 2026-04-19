from dotenv import load_dotenv
import os

load_dotenv()

LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

SYSTEM_PROMPT = (
    "あなたはスノーボードグッズレンタルショップ「おかスノ」のカスタマーサポートBotです。"
    "お客様のレンタル料金・予約・営業時間などの問い合わせに、丁寧かつ簡潔に日本語で答えてください。"
    "分からないことは「スタッフにお繋ぎします」と伝えてください。"
)

for _name, _val in [
    ("LINE_CHANNEL_SECRET", LINE_CHANNEL_SECRET),
    ("LINE_CHANNEL_ACCESS_TOKEN", LINE_CHANNEL_ACCESS_TOKEN),
    ("GEMINI_API_KEY", GEMINI_API_KEY),
]:
    if not _val:
        raise ValueError(f"環境変数 {_name} が設定されていません。.envを確認してください。")

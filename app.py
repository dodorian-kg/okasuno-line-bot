import logging
from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from config import LINE_CHANNEL_SECRET, LINE_CHANNEL_ACCESS_TOKEN, HANDOFF_PHRASE
from gemini_client import get_gemini_response
from notifier import notify_staff
from supabase_client import set_pending_handoff, peek_pending_handoff, delete_pending_handoff

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)
handler = WebhookHandler(LINE_CHANNEL_SECRET)
configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)

AFFIRMATIVE_TOKENS = ("yes", "y", "はい", "お願い", "おねがい", "ok", "了解", "うん", "繋い", "つない")
NEGATIVE_TOKENS = ("no", "n", "いいえ", "結構", "大丈夫", "やめ", "キャンセル")


def _is_affirmative(text: str) -> bool:
    t = text.strip().lower()
    return any(tok in t for tok in AFFIRMATIVE_TOKENS)


def _is_negative(text: str) -> bool:
    t = text.strip().lower()
    return any(tok in t for tok in NEGATIVE_TOKENS)


def _reply(event, text: str) -> None:
    with ApiClient(configuration) as api_client:
        MessagingApi(api_client).reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=text)],
            )
        )
    logger.info(f"返信: {text}")


@app.route("/health")
def health():
    return {"status": "ok"}


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        logger.warning("署名検証失敗")
        abort(400)
    return "OK"


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_text = event.message.text
    user_id = getattr(event.source, "user_id", None)
    logger.info(f"受信: {user_text} source={event.source}")

    if user_id and (_is_affirmative(user_text) or _is_negative(user_text)):
        pending = peek_pending_handoff(user_id)
        if pending:
            if _is_affirmative(user_text):
                notify_staff(pending["original_question"], pending["bot_reply"])
                delete_pending_handoff(user_id)
                _reply(event, "スタッフに連絡しました。しばらくお待ちください。")
                return
            if _is_negative(user_text):
                delete_pending_handoff(user_id)
                _reply(event, "承知しました。ほかにご質問があればどうぞ。")
                return

    try:
        reply_text = get_gemini_response(user_text)
    except Exception as e:
        logger.error(f"Gemini APIエラー: {e}")
        reply_text = "申し訳ありません、現在応答できません。しばらくお待ちください。"

    if HANDOFF_PHRASE in reply_text and user_id:
        try:
            set_pending_handoff(user_id, user_text, reply_text)
            logger.info(f"pending_handoff set for {user_id}")
        except Exception as e:
            logger.error(f"pending_handoff保存失敗: {e}")

    _reply(event, reply_text)


if __name__ == "__main__":
    logger.info("サーバー起動")
    app.run(port=5000)

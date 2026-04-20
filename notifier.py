import logging
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    PushMessageRequest,
    TextMessage,
)
from config import LINE_CHANNEL_ACCESS_TOKEN, ADMIN_LINE_TARGET_ID

logger = logging.getLogger(__name__)

_configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)


def notify_staff(user_text: str, bot_text: str) -> None:
    if not ADMIN_LINE_TARGET_ID:
        logger.warning("ADMIN_LINE_TARGET_ID 未設定のためスタッフ通知をスキップ")
        return

    body = (
        "🔔 スタッフ対応依頼\n"
        "—\n"
        "【お客様の質問】\n"
        f"{user_text}\n"
        "—\n"
        "【Bot の返答】\n"
        f"{bot_text}"
    )

    try:
        with ApiClient(_configuration) as api_client:
            MessagingApi(api_client).push_message(
                PushMessageRequest(
                    to=ADMIN_LINE_TARGET_ID,
                    messages=[TextMessage(text=body)],
                )
            )
        logger.info("スタッフ通知を送信しました")
    except Exception as e:
        logger.error(f"スタッフ通知の送信に失敗: {e}")

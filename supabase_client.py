from __future__ import annotations

import logging
from collections import OrderedDict
from datetime import datetime, timedelta, timezone
from supabase import create_client
from config import SUPABASE_URL, SUPABASE_KEY

logger = logging.getLogger(__name__)

_client = create_client(SUPABASE_URL, SUPABASE_KEY)


def get_all_faqs() -> "OrderedDict[str, list[dict]]":
    res = _client.table("faqs").select("question, answer, category").order("category").execute()
    rows = res.data or []
    grouped: "OrderedDict[str, list[dict]]" = OrderedDict()
    for row in rows:
        grouped.setdefault(row["category"], []).append(row)
    logger.info(f"faqs fetched: {len(rows)} rows / {len(grouped)} categories")
    return grouped


def format_faqs_for_prompt(grouped: "OrderedDict[str, list[dict]]") -> str:
    lines: list[str] = []
    for category, items in grouped.items():
        lines.append(f"### {category}")
        for item in items:
            lines.append(f"Q: {item['question']}")
            lines.append(f"A: {item['answer']}")
        lines.append("")
    return "\n".join(lines).strip()


PENDING_HANDOFF_TTL_MINUTES = 10


def set_pending_handoff(user_id: str, original_question: str, bot_reply: str) -> None:
    res = _client.table("pending_handoffs").upsert(
        {
            "user_id": user_id,
            "original_question": original_question,
            "bot_reply": bot_reply,
        }
    ).execute()
    logger.info(f"pending_handoff upsert response: data={res.data}")


def peek_pending_handoff(user_id: str) -> dict | None:
    res = (
        _client.table("pending_handoffs")
        .select("user_id, original_question, bot_reply, created_at")
        .eq("user_id", user_id)
        .execute()
    )
    rows = res.data or []
    if not rows:
        return None

    row = rows[0]
    created = datetime.fromisoformat(row["created_at"].replace("Z", "+00:00"))
    if datetime.now(timezone.utc) - created > timedelta(minutes=PENDING_HANDOFF_TTL_MINUTES):
        logger.info(f"pending_handoff expired for {user_id}")
        _client.table("pending_handoffs").delete().eq("user_id", user_id).execute()
        return None
    return row


def delete_pending_handoff(user_id: str) -> None:
    _client.table("pending_handoffs").delete().eq("user_id", user_id).execute()
    logger.info(f"pending_handoff deleted for {user_id}")

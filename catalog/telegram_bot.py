import json
import logging
import urllib.request
import urllib.error

from django.conf import settings

logger = logging.getLogger(__name__)


def send_message(chat_id, text, reply_to=None):
    """Send a message via Telegram Bot API. Returns the message_id or None."""
    token = settings.TELEGRAM_BOT_TOKEN
    if not token:
        logger.warning("TELEGRAM_BOT_TOKEN is not configured")
        return None

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
    }
    if reply_to:
        payload["reply_to_message_id"] = reply_to

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            if result.get("ok"):
                return result["result"]["message_id"]
    except (urllib.error.URLError, json.JSONDecodeError, KeyError) as e:
        logger.error("Telegram send_message error: %s", e)

    return None


def send_to_admin(session, message_text):
    """Forward a visitor message to the admin Telegram chat."""
    chat_id = settings.TELEGRAM_CHAT_ID
    if not chat_id:
        logger.warning("TELEGRAM_CHAT_ID is not configured")
        return None

    name = session.visitor_name or "Гість"
    text = (
        f"<b>💬 Нове повідомлення від {name}</b>\n\n"
        f"{message_text}\n\n"
        f"🔗 Сесія #{session.id}"
    )

    reply_to = session.telegram_message_id
    message_id = send_message(chat_id, text, reply_to=reply_to)

    if message_id:
        session.telegram_message_id = message_id
        session.save(update_fields=["telegram_message_id"])

    return message_id

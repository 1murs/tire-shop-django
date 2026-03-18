import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from ..models import ChatSession, ChatMessage


@require_POST
def chat_send(request):
    """Handle visitor chat message (AJAX)."""
    from .. import telegram_bot

    try:
        data = json.loads(request.body)
        text = data.get("text", "").strip()
        name = data.get("name", "").strip()

        if not text:
            return JsonResponse({"success": False, "error": "Порожнє повідомлення"})

        if not request.session.session_key:
            request.session.create()

        session_key = request.session.session_key
        chat_session, created = ChatSession.objects.get_or_create(
            session_key=session_key,
            defaults={"visitor_name": name, "is_active": True},
        )

        if name and chat_session.visitor_name != name:
            chat_session.visitor_name = name
            chat_session.save(update_fields=["visitor_name"])

        msg = ChatMessage.objects.create(
            session=chat_session,
            sender=ChatMessage.SENDER_VISITOR,
            text=text,
        )

        telegram_bot.send_to_admin(chat_session, text)

        return JsonResponse({
            "success": True,
            "message": {
                "id": msg.id,
                "sender": msg.sender,
                "text": msg.text,
                "created_at": msg.created_at.isoformat(),
            },
        })
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


def chat_messages(request):
    """Return chat messages for current session (AJAX, polling)."""
    if not request.session.session_key:
        return JsonResponse({"messages": []})

    try:
        chat_session = ChatSession.objects.get(session_key=request.session.session_key)
    except ChatSession.DoesNotExist:
        return JsonResponse({"messages": []})

    after = request.GET.get("after")
    qs = chat_session.messages.all()
    if after:
        qs = qs.filter(id__gt=after)

    messages = [
        {
            "id": m.id,
            "sender": m.sender,
            "text": m.text,
            "created_at": m.created_at.isoformat(),
        }
        for m in qs
    ]
    return JsonResponse({"messages": messages})


@csrf_exempt
@require_POST
def chat_telegram_webhook(request):
    """Handle incoming Telegram webhook (admin replies)."""
    import logging
    logger = logging.getLogger("catalog")

    try:
        payload = json.loads(request.body)
        logger.warning("Webhook received: %s", json.dumps(payload, ensure_ascii=False)[:500])

        message = payload.get("message", {})

        reply = message.get("reply_to_message")
        if not reply:
            logger.warning("Webhook: no reply_to_message")
            return JsonResponse({"ok": True})

        reply_message_id = reply.get("message_id")
        text = message.get("text", "").strip()
        logger.warning("Webhook: reply_to=%s, text=%s", reply_message_id, text)

        if not text or not reply_message_id:
            return JsonResponse({"ok": True})

        import re
        chat_session = None
        try:
            chat_session = ChatSession.objects.get(telegram_message_id=reply_message_id)
            logger.warning("Webhook: found session by tg_msg_id #%s", chat_session.id)
        except ChatSession.DoesNotExist:
            # Try to find session by "Сесія #N" in bot message text
            reply_text = reply.get("text", "")
            match = re.search(r"Сесія #(\d+)", reply_text)
            if match:
                try:
                    chat_session = ChatSession.objects.get(id=int(match.group(1)))
                    logger.warning("Webhook: found session by text #%s", chat_session.id)
                except ChatSession.DoesNotExist:
                    pass

        if not chat_session:
            logger.warning("Webhook: no session for tg_msg_id=%s", reply_message_id)
            return JsonResponse({"ok": True})

        ChatMessage.objects.create(
            session=chat_session,
            sender=ChatMessage.SENDER_ADMIN,
            text=text,
        )
        logger.warning("Webhook: admin message saved")

        return JsonResponse({"ok": True})
    except (json.JSONDecodeError, KeyError) as e:
        logger.warning("Webhook error: %s", e)
        return JsonResponse({"ok": True})

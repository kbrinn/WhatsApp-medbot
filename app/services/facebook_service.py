import logging

import requests
import structlog
from decouple import config

logger = structlog.get_logger()

ACCESS_TOKEN = config("FB_ACCESS_TOKEN")
PHONE_NUMBER_ID = config("FB_PHONE_NUMBER_ID")


def send_message(to_number: str, body_text: str) -> None:
    """Send a WhatsApp message through Facebook's Cloud API."""
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": body_text},
    }
    masked_to = f"{to_number[:2]}***" if to_number else "***"
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        message_id = None
        if isinstance(data, dict):
            message_id = data.get("messages", [{}])[0].get("id")
        logger.info("fb_message_sent", to=masked_to, message_id=message_id)
    except Exception as exc:  # pragma: no cover - network failures are not tested
        logger.error("fb_send_failed", to=masked_to, error=str(exc))

"""Minimal Telegram Bot API client."""

import logging

import httpx

logger = logging.getLogger(__name__)

TELEGRAM_API_URL = "https://api.telegram.org"
REQUEST_TIMEOUT_SECONDS = 15.0


class TelegramError(Exception):
    """Raised when the Telegram API rejects a request."""


async def send_message(bot_token: str, chat_id: str, html_text: str, link_preview: bool = False) -> None:
    """Send an HTML-formatted message to a chat.

    Args:
        bot_token: Token issued by @BotFather.
        chat_id: Target chat id.
        html_text: Message body using Telegram's HTML subset.
        link_preview: Whether Telegram should render a preview of the first link.

    Raises:
        TelegramError: If the API call fails.
    """
    await _call(
        bot_token,
        "sendMessage",
        {
            "chat_id": chat_id,
            "text": html_text,
            "parse_mode": "HTML",
            "disable_web_page_preview": not link_preview,
        },
    )


async def detect_chat_id(bot_token: str) -> tuple[str, str] | None:
    """Find the most recent private chat that messaged the bot.

    The user must send any message (e.g. /start) to the bot first.

    Args:
        bot_token: Token issued by @BotFather.

    Returns:
        A ``(chat_id, display_name)`` tuple, or None if nobody messaged the bot yet.

    Raises:
        TelegramError: If the API call fails.
    """
    updates = await _call(bot_token, "getUpdates", {"limit": 100})
    for update in reversed(updates):
        message = update.get("message") or update.get("edited_message")
        if not message:
            continue
        chat = message["chat"]
        name = chat.get("first_name") or chat.get("title") or chat.get("username") or ""
        return str(chat["id"]), name
    return None


async def _call(bot_token: str, method: str, payload: dict) -> list | dict:
    """POST to a Bot API method and return its ``result`` field."""
    if not bot_token:
        raise TelegramError("token do bot não configurado")
    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
            response = await client.post(f"{TELEGRAM_API_URL}/bot{bot_token}/{method}", json=payload)
        body = response.json()
    except (httpx.HTTPError, ValueError) as error:
        raise TelegramError(f"falha ao contatar o Telegram: {error.__class__.__name__}") from error
    if not body.get("ok"):
        raise TelegramError(body.get("description", f"HTTP {response.status_code}"))
    return body["result"]

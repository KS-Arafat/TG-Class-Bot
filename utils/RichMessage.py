import httpx
from telegram import Update
from telegram.ext import ContextTypes


async def SendRichHTML(
    update: Update, context: ContextTypes.DEFAULT_TYPE, msg: str
) -> None:
    chat_id = update.message.chat_id
    token = update._bot.token
    payload = {
        "chat_id": chat_id,
        "rich_message": {"html": msg},
    }

    url = f"https://api.telegram.org/bot{token}/sendRichMessage"
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=payload)
        data = resp.json()

    if not data.get("ok"):
        print("Telegram error:", data)
    return data


async def SendRichMARKDOWN(
    update: Update, context: ContextTypes.DEFAULT_TYPE, msg: str
) -> None:
    chat_id = update.message.chat_id
    token = update._bot.token
    payload = {
        "chat_id": chat_id,
        "rich_message": {"markdown": msg},
    }

    url = f"https://api.telegram.org/bot{token}/sendRichMessage"
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=payload)
        data = resp.json()

    if not data.get("ok"):
        print("Telegram error:", data)
    return data

import httpx
from telegram import Update
from telegram.ext import ContextTypes


async def SendRichHTMLTable(
    update: Update, context: ContextTypes.DEFAULT_TYPE, msg: str
) -> None:
    chat_id = update.message.chat_id
    token = update._bot.token
    payload = {
        "chat_id": chat_id,
        "rich_message": {
            # "markdown": "| Metric | Value |\n|:-------|------:|\n| Speed  | **42** <sup>ms</sup> |\n| Status | <tg-spoiler>ready</tg-spoiler> |"
            "html": msg.replace("<table>", "<table bordered striped>").replace(
                "<td>", '<td align="center">'
            )
        },
    }

    url = f"https://api.telegram.org/bot{token}/sendRichMessage"
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=payload)
        data = resp.json()

    if not data.get("ok"):
        print("Telegram error:", data)
    return data

from typing import Final
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

# Constant
# BOT_TOKEN
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
if BOT_TOKEN == None:
    raise "BOT_TOKEN NOT FOUND"


async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Start Command")
    return


async def new_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("New Command")
    return


async def cancel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Cancel Command")
    return


async def del_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Del Command")
    return


async def show_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Show Command")
    return


async def next_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Next Command")
    return


async def today_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Today Command")
    return


async def tmrw_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Tmrw Command")
    return


async def post_init(application: Application) -> None:
    await application.bot.set_my_commands(
        [
            ("start", "Shows Welcome Message"),
            ("new", "Creates New Routine"),
            ("cancel", "Cancels Routine Creation"),
            ("del", "Deletes Saved Routine"),
            ("show", "Shows Saved Routine"),
            ("next", "Shows Next Class wrt to Current Time"),
            ("today", "Shows All the Classes for That Day"),
            ("tmrw", "Shows All the Classes for the Next Day"),
        ]
    )


if __name__ == "__main__":
    print("Starting Telegram Bot ..........")
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("new", new_cmd))
    app.add_handler(CommandHandler("cancel", cancel_cmd))
    app.add_handler(CommandHandler("del", del_cmd))
    app.add_handler(CommandHandler("show", show_cmd))
    app.add_handler(CommandHandler("next", next_cmd))
    app.add_handler(CommandHandler("today", today_cmd))
    app.add_handler(CommandHandler("tmrw", tmrw_cmd))

    app.run_polling(poll_interval=3)

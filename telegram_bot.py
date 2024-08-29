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
from tinydb import TinyDB, Query
import prettytable as pt


# Constant
DB_PATH: Final = "./Routine.json"

# BOT_TOKEN
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
if BOT_TOKEN == None:
    raise "BOT_TOKEN NOT FOUND"

# TinyDB
# For Query
q: Final = Query()

# Routine Table and Course Table
# Structure:
# {"id": "149523456","crs_code": "CHE101","sec": "9","day": "RA","starts": "08:00AM",
#  "ends": "09:15AM","room": "SAC402","faculty": "MIO",}
rtable: Final = TinyDB(DB_PATH).table("ROUTINE")

# {"code": "CHE101","title": "General Chemistry"}
ctable: Final = TinyDB(DB_PATH).table("COURSE")

ptable = pt.PrettyTable(["Code", "Sec", "Day", "Starts", "Room", "Facu"])


# Parse Raw string of rds Routine Data and make it list usable
def parse_crsec(sr: str):
    try:
        sr = sr.replace(" ", "")

        for i in range(len(sr) - 1):
            if sr[i].isupper() and sr[i + 1].islower():
                # print(sr[i])
                sr1 = sr[0:i]
                sr2 = sr[i:]
                break
        # print(sr1)
        # print(sr2)

        for i in range(3, len(sr2) - 1):
            if sr2[i].isdigit() and sr2[i + 1].isdigit():
                if sr2[i - 2] in "MWRAST":
                    sr3 = sr2[0 : i - 2]
                    sr4 = sr2[i - 2 : i]
                    sr5 = sr2[i:]
                else:
                    sr3 = sr2[0 : i - 1]
                    sr4 = sr2[i - 1 : i]
                    sr5 = sr2[i:]
                break

        for i in range(1, len(sr3) - 1):
            if sr3[i].islower() and sr3[i + 1].isupper():
                sr3 = sr3[: i + 1] + " " + sr3[i + 1 :]

        sr3 = " & ".join(sr3.split("&"))
        # print(sr4)
        # print(sr5)

        for i in range(len(sr5) - 1):
            if sr5[i].isupper() and sr5[i + 1].isupper():
                sr6 = sr5[: i + 2]
                sr7 = sr5[i + 2 :]
                break

        # print(sr6)
        for i in range(len(sr6) - 1):
            if sr7[i].isupper() and sr7[i + 1].isupper():
                sr8 = sr7[: i + 2]
                sr9 = sr7[i + 2 :]
                break

        # print(sr8)
        # print(sr9)

        for i in range(len(sr9) - 1):
            if sr9[i].isdigit():
                sr10 = sr9[: i + 3]
                sr11 = sr9[i + 3 :]
                break

        hit = False
        for i in range(4, len(sr1)):
            # print(cr[i], cr[i].isalpha())
            if sr1[i].isalpha():
                # print("hit")
                cls = sr1[: i + 1]
                sec = sr1[i + 1 :]
                hit = True
                break
        if not hit:
            if sr1.startswith("PHR") or sr1.startswith("EMP"):
                cls = sr1[:7]
                sec = sr1[7:]

            else:
                cls = sr1[:6]
                sec = sr1[6:]

        return [cls, sec, sr3, sr4, sr6, sr8, sr10, sr11]

    except:
        return ""


# Parsing to make it list of dict to use it with tinydb more easier
def json_parse(prsd: list[list], uid: str):

    routine = []
    courses = []

    for r in prsd:
        # print(len(r))
        if len(r) != 8:
            continue
        routine.append(
            {
                "id": str(uid),
                "crs_code": r[0],
                "sec": r[1],
                "day": r[3],
                "starts": r[4],
                "ends": r[5],
                "room": r[6],
                "faculty": r[7],
            }
        )
        courses.append({"code": r[0], "title": r[2]})
    return routine, courses


async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_markdown_v2(
        """*__Welcome to NSU Class Notifier Bot__*
_Copy Routine From RDS By Selecting the Whole Table_
_Paste It after `/new` Command_
"""
    )
    return


async def new_cmd_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    # Limitng 1 Routine Per User
    if rtable.count(q.id == str(user_id)) != 0:
        await update.message.reply_text(f"Delete Saved Routine First!!")
        return ConversationHandler.END
    await update.message.reply_text("Paste the Routine Table:")
    return 1


async def new_cmd_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    routine_content = update.message.text
    user_id = update.message.from_user.id

    # print(routine_content)

    rl = routine_content.replace("\t", " ").split("\n")
    len_rl = len(rl)
    rlf = [parse_crsec(r) for r in rl if r != ""]
    len_rlf = len(rlf)
    rdata, cdata = json_parse(rlf, user_id)

    len_table = len(rtable.insert_multiple(rdata))
    for c in cdata:
        ctable.upsert(c, q.code == c["code"])

    await update.message.reply_markdown_v2(
        f"""📜  *Routine has been saved*
    🌟  Out of *_{len_rl}_* rows
    🌟  *_{len_rlf}_* rows successfully formatted
    🌟  *_{len_table}_* rows inserted to Database
    """
    )
    return ConversationHandler.END


async def cancel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Routine creation cancelled.")
    return ConversationHandler.END


async def del_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    rtable.remove(q.id == str(uid))
    await update.message.reply_text(f"Routine Deleted!!")
    return


async def show_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    rdata = rtable.search(q.id == str(uid))
    if len(rdata) == 0:
        await update.message.reply_text(f"No Routine Found For the User")
        return

    ptable.clear_rows()
    for r in rdata:
        ptable.add_row(
            [
                r["crs_code"],
                r["sec"],
                r["day"],
                r["starts"],
                r["room"],
                r["faculty"],
            ]
        )

    await update.message.reply_html(f"<i>Routine:</i>\n<pre>{ptable}</pre>")
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


async def dev_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_markdown_v2(update.message.text)
    return


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update "{update.message.text}"  \nError: {context.error}')


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

    # Multi-State Handler
    new_conversation = ConversationHandler(
        entry_points=[CommandHandler("new", new_cmd_entry)],
        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, new_cmd_content)],
        },
        fallbacks=[CommandHandler("cancel", cancel_cmd)],
    )

    app.add_handler(new_conversation)
    app.add_handler(CommandHandler("cancel", cancel_cmd))
    app.add_handler(CommandHandler("del", del_cmd))
    app.add_handler(CommandHandler("show", show_cmd))
    app.add_handler(CommandHandler("next", next_cmd))
    app.add_handler(CommandHandler("today", today_cmd))
    app.add_handler(CommandHandler("tmrw", tmrw_cmd))

    # /dev for developer
    app.add_handler(CommandHandler("dev", dev_cmd))
    app.add_error_handler(error_handler)

    app.run_polling(poll_interval=3)

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
import prettytable as pt
from datetime import UTC, timedelta, datetime
import pickle
import lmdb
from utils.RichMessage import SendRichHTML, SendRichMARKDOWN

# Constant
DB_PATH: Final = "./DATABASE_DO_NOT_DELETE"


# bytes transformer
dumper = pickle.dumps
loader = pickle.loads

# Lightning Memory-Mapped Database
env = lmdb.open(DB_PATH, map_size=(10**8))

# Read TXN
rtxn = env.begin(write=False)

# Day ShortHand according to RDS
day_sh = {
    "Sun": "S",
    "Tue": "T",
    "Mon": "M",
    "Wed": "W",
    "Thu": "R",
    "Fri": "F",
    "Sat": "A",
}
# Possible Day Pairs in RDS
day_pairs = {"S": "ST", "T": "ST", "M": "MW", "W": "MW", "R": "RA", "A": "RA", "F": "F"}

ptable = pt.PrettyTable(["Code", "Sec", "Day", "Starts", "Room", "Facu"])


def logging(cmmd: str, update: Update = None, flush=False):

    if not hasattr(logging, "_buffer"):
        logging._buffer = []
    tn = datetime.now(UTC) + timedelta(hours=6)

    if not flush:
        log = {
            "Time": tn.strftime("%d/%m/%Y, %I:%M %p"),
            "Name": update.message.from_user.name,
            "ID": update.message.from_user.id,
            "CMD": cmmd,
        }
        print(log)
        logging._buffer.append(log)
    else:
        logging._buffer.append(cmmd + tn.strftime("%d/%m/%Y, %I:%M %p"))

    if len(logging._buffer) >= 3 or flush:
        with open(
            DB_PATH + f"/BOT_{tn.strftime('%d-%m-%Y')}.log", "a", encoding="utf-8"
        ) as f:
            f.write("\n".join(str(item) for item in logging._buffer) + "\n")

        logging._buffer.clear()


# Refresh rtxn
def refresh_rtxn(env):
    global rtxn
    rtxn.abort()
    rtxn = env.begin(write=False)


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

        rdata: dict[str, str] = {
            "crs_code": r[0],
            "sec": r[1],
            "day": r[3],
            "starts": r[4],
            "ends": r[5],
            "room": r[6],
            "faculty": r[7],
        }

        if not (
            rdata["sec"].isnumeric()
            and len(rdata["day"]) <= 2
            and len(rdata["starts"]) == 7
            and len(rdata["ends"]) == 7
            and (
                rdata["room"].startswith("NAC")
                or rdata["room"].startswith("SAC")
                or rdata["room"].startswith("LIB")
                or rdata["room"].startswith("AUD")
            )
        ):
            continue

        routine.append(rdata)
        courses.append({"code": r[0], "title": r[2]})

    return uid, routine, courses


def get_day_classes(UID: str, today: bool):

    if today == False:
        dt = datetime.now(UTC) + timedelta(days=1, hours=6)
    else:
        dt = datetime.now(UTC) + timedelta(hours=6)

    td = dt.strftime("%a")[:3]
    if td == "Fri":
        return []

    sh = day_sh[td]
    pairs = day_pairs[sh]

    _bytes = rtxn.get(dumper(UID))
    if _bytes is None:
        return []

    classes = [c for c in loader(_bytes) if c["day"] == pairs or c["day"] == sh]

    return classes


def build_table(rtable):

    ptable.clear_rows()
    for r in rtable:
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
    return ptable


def exact_time_hour(tn: str):
    h, m = [int(x) for x in tn[:5].split(":")]
    is_pm = tn[5:] == "PM"

    if h == 12:
        h = 12 if is_pm else 0
    elif is_pm:
        h += 12

    return h + (m / 60)


# String format of hour
def strf_hour(hours: float):
    hi = int(hours)
    hf = hours - hi
    return f"{hi:02} Hours {int(hf*60):02} Minutes"


def next_class(uid: str):

    time_gmtp6 = datetime.now(UTC) + timedelta(hours=6)

    tn = time_gmtp6.strftime("%I:%M%p")

    exhour = exact_time_hour(tn)

    # print("Test time: ", exhour)

    clss = get_day_classes(uid, True)
    if len(clss) == 0:
        return "<b>🎉 No Classes Today 🎉</b>"
    next_cls = ""
    clssdiff = 0
    temp = 24.0

    for i in range(len(clss)):
        clssi = clss[i]
        diff = exact_time_hour(clssi["starts"]) - exhour

        if temp > diff and diff >= 0:
            temp = diff
            next_cls = clssi
            clssdiff = diff

    # print(next_cls)
    if next_cls == "":
        return "<b>🎉 No More Class Today 🎉</b>"

    course_title = loader(rtxn.get(dumper(next_cls["crs_code"])))

    next_cls_detail = f"""
# ⏳ Next Class ⏳
#### {next_cls["crs_code"]} 📚 {course_title}
> Begins in {strf_hour(clssdiff)}

|-------------|----------|
|:------------|---------:|
| Room    🏢  |   {next_cls["room"]}|
| Faculty 👤  |   {next_cls["faculty"]}|
| Time    🕓  |   {next_cls["starts"]} - {next_cls["ends"]}|
| Section 🔤  |   {int(next_cls["sec"]):02}</pre>|
"""
    return next_cls_detail


async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):

    logging("/start", update)
    await update.message.reply_video("./TG_Bot_Demo.mp4")
    await update.message.reply_markdown_v2("""*__Welcome to NSU Class Notifier Bot__*
_Copy Routine From RDS Attendance By Selecting the Whole Table_
_Paste It after `/new` Command_
_If you copied from Phone📱 then chose *__Paste as plain text__* option_
""")
    return


async def new_cmd_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):

    logging("/new", update)
    user_id = update.message.from_user.id.__str__()

    # Limitng 1 Routine Per User
    raw_bytes = rtxn.get(dumper(user_id))

    if raw_bytes is not None:
        await update.message.reply_markdown_v2("> 🗑 Delete Saved Routine First\\!")
        return ConversationHandler.END
    await update.message.reply_markdown_v2("> 📄 Paste the Routine Table")
    return 1


async def new_cmd_content(
    update: Update, context: ContextTypes.DEFAULT_TYPE, override_msg: str = ""
):

    routine_content = ""
    if len(override_msg) != 0:
        routine_content = override_msg
    else:
        routine_content = update.message.text

    user_id = update.message.from_user.id.__str__()

    # print(routine_content)

    rl = routine_content.replace("\t", " ").split("\n")
    len_rl = len(rl)
    rlf = [parse_crsec(r) for r in rl if r != ""]
    len_rlf = len(rlf)
    rid, rdata, cdata = json_parse(rlf, user_id)

    with env.begin(write=True) as txn:
        txn.put(dumper(rid), dumper(rdata))
        for c in cdata:
            txn.put(dumper(c["code"]), dumper(c["title"]))

    refresh_rtxn(env)
    await update.message.reply_markdown_v2(f"""📜  __*Routine has been saved*__
    ✨  Out of *_{len_rl}_* rows
    🌟  *_{len_rlf}_* rows successfully formatted
    ✴️  *_{len(rdata)}_* rows inserted to Database
    """)
    return ConversationHandler.END


async def cancel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):

    logging("/cancel", update)
    await update.message.reply_markdown_v2("> ❌ *Routine creation cancelled\\.*")
    return ConversationHandler.END


async def del_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):

    logging("/del", update)
    uid = update.message.from_user.id.__str__()
    with env.begin(write=True) as wtxn:
        wtxn.delete(dumper(uid))

    refresh_rtxn(env)
    await update.message.reply_markdown_v2(f"> ☠️ *Routine Deleted\\!\\!*")
    return


async def show_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):

    logging("/show", update)
    uid = update.message.from_user.id.__str__()

    _bytes = rtxn.get(dumper(uid))

    if _bytes is None:
        await update.message.reply_markdown_v2(
            "🎉 __No Routine Found For the User__ 🎉"
        )
        return

    result = loader(_bytes)
    await SendRichHTML(
        update,
        context,
        f"""<blockquote><h1>Your Saved Routine</h1></blockquote>
    {build_table(result).get_html_string().replace("<table>", "<table bordered striped>").replace(
                "<td>", '<td align="center">'
            )}""",
    )
    return


async def next_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):

    logging("/next", update)
    uid = update.message.from_user.id.__str__()
    # await update.message.reply_html(next_class(uid))
    await SendRichMARKDOWN(update, context, next_class(uid))
    return


async def today_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):

    logging("/today", update)
    uid = update.message.from_user.id.__str__()

    todays_class = get_day_classes(uid, True)

    if len(todays_class) != 0:
        await SendRichHTML(
            update,
            context,
            f"""
<blockquote><h1> Class List For Today </h1></blockquote>
{build_table(todays_class).get_html_string().replace("<table>", "<table bordered striped>").replace(
                "<td>", '<td align="center">'
            )}
""",
        )
    else:
        await SendRichHTML(
            update,
            context,
            "<blockquote><h1>🎉 No Classes Today 🎉</h1></blockquote>",
        )
    return


async def tmrw_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):

    logging("/tmrw", update)
    uid = update.message.from_user.id.__str__()

    tmrws_class = get_day_classes(uid, False)

    if len(tmrws_class) != 0:
        await SendRichHTML(
            update,
            context,
            f"""
<blockquote><h1>Class List For Tomorrow </h1></blockquote>
{build_table(tmrws_class).get_html_string().replace("<table>", "<table bordered striped>").replace(
                "<td>", '<td align="center">'
            )}
""",
        )
    else:
        await SendRichHTML(
            update,
            context,
            "<blockquote><h1>🎉 <b>No Classes Tomomrrow</b> 🎉</h1></blockquote>",
        )
    return


async def dev_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):

    logging("/dev", update)
    await update.message.reply_html(
        "\U0001f916 Creating Dummy Data for Testing \U0001f916\n\n"
    )
    dummy_routine = """
MAT361  1  Probability and Statistics  MW  08:00 AM  09:30 AM  SAC208  AdS1
MAT361  2  Probability and Statistics  MW  11:20 AM  12:50 PM  SAC208  AdS1
MAT361  3  Probability and Statistics  MW  02:40 PM  04:10 PM  SAC208  AdS1
MAT361  4  Probability and Statistics  MW  06:00 PM  07:30 PM  SAC208  AdS1
MAT361  5  Probability and Statistics  MW  08:00 PM  09:30 PM  SAC208  AdS1
MAT361  6  Probability and Statistics  MW  10:00 PM  11:30 PM  SAC208  AdS1
MAT361  7  Probability and Statistics  MW  12:00 AM  01.30 AM  SAC208  AdS1
MAT361  1  Probability and Statistics  RA  08:00 AM  09:30 AM  SAC208  AdS1
MAT361  2  Probability and Statistics  RA  11:20 AM  12:50 PM  SAC208  AdS1
MAT361  3  Probability and Statistics  RA  02:40 PM  04:10 PM  SAC208  AdS1
MAT361  4  Probability and Statistics  RA  06:00 PM  07:30 PM  SAC208  AdS1
MAT361  5  Probability and Statistics  RA  08:00 PM  09:30 PM  SAC208  AdS1
MAT361  6  Probability and Statistics  RA  10:00 PM  11:30 PM  SAC208  AdS1
MAT361  7  Probability and Statistics  RA  12:00 AM  01.30 AM  SAC208  AdS1
MAT361  1  Probability and Statistics  ST  08:00 AM  09:30 AM  SAC208  AdS1
MAT361  2  Probability and Statistics  ST  11:20 AM  12:50 PM  SAC208  AdS1
MAT361  3  Probability and Statistics  ST  02:40 PM  04:10 PM  SAC208  AdS1
MAT361  4  Probability and Statistics  ST  06:00 PM  07:30 PM  SAC208  AdS1
MAT361  5  Probability and Statistics  ST  08:00 PM  09:30 PM  SAC208  AdS1
MAT361  6  Probability and Statistics  ST  10:00 PM  11:30 PM  SAC208  AdS1
MAT361  7  Probability and Statistics  ST  12:00 AM  01.30 AM  SAC208  AdS1
"""
    await del_cmd(update, context)
    await new_cmd_content(update, context, dummy_routine)
    await update.message.reply_html("\U0001f916 Dummy Routine Created \U0001f916\n\n")
    return


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update "{update.message.text}"  \nError: {context.error}')


async def post_init(application: Application) -> None:
    await application.bot.set_my_commands(
        [
            # ("start", "Shows Welcome Message"), # Don't Want to Include
            ("new", "Creates New Routine"),
            ("cancel", "Cancels Routine Creation"),
            ("del", "Deletes Saved Routine"),
            ("show", "Shows Saved Routine"),
            ("next", "Shows Next Class wrt to Current Time"),
            ("today", "Shows All the Classes for That Day"),
            ("tmrw", "Shows All the Classes for the Next Day"),
        ]
    )


def TG_Class_Bot(Prod=False):
    try:
        # BOT_TOKEN
        load_dotenv()
        BOT_TOKEN = os.getenv("BOT_TOKEN") if Prod else os.getenv("BOT_TOKEN_DEV")
        if BOT_TOKEN == None:
            raise "BOT_TOKEN NOT FOUND"

        print(
            f"Starting Telegram Bot {"PRODUCTION" if Prod else "DEVELOPMENT"} .........."
        )
        logging("Started Bot At: ", flush=True)
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

    except Exception as e:
        print("Error: ", e.__str__())
        logging(f"Error Occured\t{e.__str__()}\tAt: ", flush=True)

    finally:
        print("\nSTOPPING BOT.....")
        logging("Stopped Bot At: ", flush=True)
        rtxn.abort()
        env.close()

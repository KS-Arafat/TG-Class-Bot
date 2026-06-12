# Telegram Bot For Class Routine

[![Python](https://img.shields.io/badge/python-3.12-blue?logo=python)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/docker-supported-blue?logo=docker&logoColor=white)](https://www.docker.com/)
[![Docker Compose](https://img.shields.io/badge/docker%20compose-supported-blue?logo=docker&)](https://docs.docker.com/compose/)
[![python-telegram-bot](https://img.shields.io/pypi/v/python-telegram-bot?label=python-telegram-bot&style=flat-square&logo=telegram)](https://pypi.org/project/python-telegram-bot/)
[![python-dotenv](https://img.shields.io/pypi/v/python-dotenv?label=python-dotenv&style=flat-square&logo=dotenv)](https://pypi.org/project/python-dotenv/)
[![prettytable](https://img.shields.io/pypi/v/prettytable?label=prettytable&style=flat-square)](https://pypi.org/project/prettytable/)
[![lmdb](https://img.shields.io/pypi/v/lmdb?label=lmdb&style=flat-square)](https://pypi.org/project/lmdb/)
[![uv](https://img.shields.io/pypi/v/uv?label=uv&style=flat-square&logo=uv)](https://pypi.org/project/uv/)

##

### ***Intro***

---
This is a Telegram Bot written in Python as NSU Class Reminder using [Python-telegram-bot](https://github.com/python-telegram-bot) library.

### ***Features:***

---

- Copy/Paste Routine and Bot will parse it

- Quick Query For Class info on the go

- Provides Class Info with respect to current time

### ***Commands:***

---

|`Command` | _Description                           |
|--------- | -------------------------------------- |
|`/start`  |   Shows Welcome Message                |
|`/new`    | Creates New Routine                    |
|`/cancel` | Cancels Routine Creation               |
|`/del`    | Deletes Saved Routine                  |
|`/show`   | Shows Saved Routine                    |
|`/next`   | Shows Next Class wrt to Current Time   |
|`/today`  | Shows All the Classes for That Day     |
|`/tmrw`   | Shows All the Classes for the Next Day |

### ***Deploy***

---
`git clone https://github.com/KS-Arafat/Class_Routine_TG_Bot.git`

#### **or**

Download the [Zip](https://github.com/KS-Arafat/Class_Routine_TG_Bot/archive/refs/heads/main.zip) & [Unzip](https://www.7-zip.org/)

```bash
cd Class_Routine_TG_Bot
echo 'BOT_TOKEN = ""' > .env
pip install -r Requirement.txt
```

But before we run the script, we have to get Bot Token from Telegram

### ***Obtain Your Bot Token***

---

- In this context, a token is a string that authenticates your bot (not your account) on the bot API. Each bot has a unique token which can also be revoked at any time via **@BotFather**.

- Obtaining a token is as simple as contacting **@BotFather**, issuing the /newbot command and following the steps until you're given a new token. You can find a step-by-step guide here.

- Your token will look something like this:

2035864719:abcdeer12378fsd659labJDRSJjhGHDGJ5

⚠️ **Warning: Make sure to save your token in a secure place, treat it like a password and don't share it with anyone.**

#### Copy the Token and Paste In `.env` and assign it to `BOT_TOKEN` environment variable like this

```js
BOT_TOKEN=2035864719:abcdeer12378fsd659labJDRSJjhGHDGJ5 
```

### Finally Run

```bash
python telegram_bot.py
```

### Deploy with docker

```bash
docker build -t tg-class-bot . 
docker run -d -p 8000:80 --env-file .env --restart unless-stopped tg-class-bot
```

### Docker Compose

Create or update `.env` with your bot token:

```bash
echo 'BOT_TOKEN=YOUR_BOT_TOKEN_HERE' > .env
```

Start the bot with Docker Compose:

```bash
docker compose up -d --build
```

This will build the image and run the container. The LevelDB database folder `DATABASE_DO_NOT_DELETE` is mounted from the host, so your data is persisted outside the container.

Stop the bot:

```bash
docker compose down
```

If your system uses the legacy compose command, use `docker-compose` instead.

***NB:* Might Have To Configure Firewall If You Get Timeout Error**

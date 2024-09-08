# Telegram Bot For Class Routine 

### ***Intro***
---
This is a Telegram Bot written <img src="https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue" height=25 />

Using [Python-telegram-bot](https://github.com/python-telegram-bot) library.

### ***Features:***
---

- Copy/Paste Routine and Bot will parse it 

- Quick Query For Class info on the go

- Provides Class Info with respect to current time


### ***Commands:***
---

`Command`| _Description_ 
-|-
`/start` |   Shows Welcome Message 
`/new`| Creates New Routine
`/cancel` | Cancels Routine Creation
`/del`| Deletes Saved Routine
`/show` | Shows Saved Routine
`/next` | Shows Next Class wrt to Current Time
`/today` | Shows All the Classes for That Day
`/tmrw` | Shows All the Classes for the Next Day


### ***Deploy***
---
`git clone https://github.com/KS-Arafat/Class_Routine_TG_Bot.git` 

__or__ 

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
BOT_TOKEN = "2035864719:abcdeer12378fsd659labJDRSJjhGHDGJ5" 
``` 

### Finally Run 

```bash
python telegram_bot.py
```

**_NB:_ Might Have To Configure Firewall If You Get Timeout Error**

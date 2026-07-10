from utils.telegram_bot import TG_Class_Bot
import sys


def main():
    prod = len(sys.argv) > 1 and sys.argv[1] == "prod"
    TG_Class_Bot(Prod=prod)


main()

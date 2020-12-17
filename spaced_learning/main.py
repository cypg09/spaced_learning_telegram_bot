import tglog
from mainclass import MainClass
from getpass import getpass

# Input your Telegram chat id (You can find it at https://t.me/get_id_bot)
MAIN_CHAT_ID = getpass("Owner's Telegram chat_id ? (To receive logs) @:")
# Input the token of a telegram bot to receive logs ; can be the same than BOT_TOKEN
# But it'll me more comfortable for you to have a logger bot
LOG_BOT_TOKEN = getpass("Log bot token ? @:")
# Input the token of the telegram bot
BOT_TOKEN = getpass("Telegram bot token ? @:")

tl = tglog.logger(MAIN_CHAT_ID,
                  LOG_BOT_TOKEN)

tl.info("main.py launched.")

main_class = MainClass(tl, BOT_TOKEN)

main_class.start()

print("Spaced Learning bot runs !")

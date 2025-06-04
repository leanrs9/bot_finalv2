import os
from keep_alive import keep_alive
from bot import bot

keep_alive()
bot.run(os.getenv("TOKEN"))

import retux
import logging

log = logging.basicConfig(level=logging.DEBUG)

bot = retux.Bot(retux.Intents.NON_PRIVILEGED)
bot.start("")

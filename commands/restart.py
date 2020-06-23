import logging
import os
import sys
from threading import Thread

from bot import persistence, updater
from utils import send
from .decorators import restricted, log


@restricted
@log
def restart(update, context):
    def stop_and_restart():
        """Gracefully stop the Updater and replace the current process with a new one"""
        persistence.flush()
        updater.stop()
        os.execl(sys.executable, sys.executable, *sys.argv)

    logging.info('Bot is restarting...')
    send('Bot is restarting...', update, context)
    Thread(target=stop_and_restart).start()
    logging.info("...and we're back")
    send("...and we're back", update, context)

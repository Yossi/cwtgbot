import logging

from telegram.ext import CommandHandler, MessageHandler
from telegram.ext import Filters
from telegram.ext import Updater, PicklePersistence

import commands
from secrets import TOKEN

logging.basicConfig(format='%(asctime)s - %(levelname)s\n%(message)s', level=logging.INFO)

persistence = PicklePersistence(filename='user.persist', on_flush=False)
updater = Updater(token=TOKEN, persistence=persistence, use_context=True)
dispatcher = updater.dispatcher

cmds = {
    'start': commands.start,
    'mlm': commands.mlm,
    'help': commands.help,
    'settings': commands.settings,
    'save': commands.save,
    'clear_save': commands.clear_save,
    'ignore': commands.ignore,
    'clear_ignore': commands.clear_ignore,
    'ping': commands.ping,
    'pong': commands.pong,
    'now': commands.now,
    'time': commands.time,
    'g_withdraw': commands.incoming,
    'g_deposit': commands.incoming,
    'warehouse': commands.warehouse,
    'w': commands.warehouse,
    'craft': commands.craft,
    'c': commands.craft,
    'brew': commands.craft,
    'stock': commands.stock,
    'alch': commands.alch,
    'other': commands.other,
    'misc': commands.misc,
    'all_stock': commands.all_stock,
    'price': commands.prices,
    'prices': commands.prices,
    'deals': commands.deals,
    'say': commands.say,  # : filters=Filters.user(user_id=LIST_OF_ADMINS,)
    'user_data': commands.user_data,
    'chat_data': commands.chat_data,  # : filters=Filters.user(user_id=LIST_OF_ADMINS,)
    'warehouse_data': commands.warehouse_data,  # : filters=Filters.user(user_id=LIST_OF_ADMINS,)
    'go': commands.destination
}
for c in cmds:
    dispatcher.add_handler(CommandHandler(c, cmds[c]))

dispatcher.add_handler(MessageHandler(Filters.regex(r'/w.*_'), commands.warehousecmd))
dispatcher.add_handler(MessageHandler(Filters.regex(r'/c.*_'), commands.craftcmd))

dispatcher.add_handler(MessageHandler(Filters.location, commands.location))
dispatcher.add_handler(MessageHandler(Filters.forwarded, commands.incoming))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, commands.incoming))


dispatcher.add_error_handler(commands.error)

from commands.decorators import restricted, log
import os
import sys
from utils import send
from threading import Thread

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

dispatcher.add_handler(CommandHandler('r', restart))

logging.info('bot started')
updater.start_polling()
updater.idle()

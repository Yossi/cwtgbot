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


for c in commands._commands:
    dispatcher.add_handler(CommandHandler(c, commands._commands[c]))

dispatcher.add_handler(MessageHandler(Filters.location, commands.location))
dispatcher.add_handler(MessageHandler(Filters.forwarded, commands.incoming))
dispatcher.add_handler(MessageHandler(Filters.text, commands.incoming))


dispatcher.add_handler(MessageHandler(Filters.regex(r'/w.*_'), commands.warehousecmd))
dispatcher.add_handler(MessageHandler(Filters.regex(r'/c.*_'), commands.craftcmd))

dispatcher.add_error_handler(commands.error)

logging.info('bot started')
updater.start_polling()
updater.idle()

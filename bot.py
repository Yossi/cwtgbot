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
    'help': help,
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
    'stock': commands.stock,
    'alch': commands.alch,
    'other': commands.other,
    'misc': commands.misc,
    'deals': commands.deals,
    'r': commands.restart,  # : filters=Filters.user(user_id=LIST_OF_ADMINS,)
    'say': commands.say,  # : filters=Filters.user(user_id=LIST_OF_ADMINS,)
    'user_data': commands.user_data,
    'chat_data': commands.chat_data,  # : filters=Filters.user(user_id=LIST_OF_ADMINS,)
    'warehouse_data': commands.warehouse_data,  # : filters=Filters.user(user_id=LIST_OF_ADMINS,)
    'go': commands.destination
}
for c in cmds:
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

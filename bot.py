import os, sys
import logging
import traceback
import pickle
from datetime import datetime, timezone
from threading import Thread
from functools import wraps
from pprint import pprint
from collections import defaultdict

from telegram import ParseMode
from telegram import ChatAction
from telegram.utils.helpers import mention_html
from telegram.ext import Updater, PicklePersistence
from telegram.ext import CommandHandler, MessageHandler
from telegram.ext import Filters

from emeryradio import emeryradio
from brains import main, warehouse_crafting
from brains import id_to_name, name_to_id
from secrets import TOKEN, LIST_OF_ADMINS

logging.basicConfig(format='%(asctime)s - %(levelname)s\n%(message)s', level=logging.INFO)

persistence = PicklePersistence(filename='user.persist')
updater = Updater(token=TOKEN, persistence=persistence, use_context=True)
dispatcher = updater.dispatcher

def error(update, context):
    # add all the dev user_ids in this list. You can also add ids of channels or groups.
    devs = LIST_OF_ADMINS
    # we want to notify the user of this problem. This will always work, but not notify users if the update is an
    # callback or inline query, or a poll update. In case you want this, keep in mind that sending the message
    # could fail
    if not update:
        return
    if update.effective_message:
        text = "Hey. I'm sorry to inform you that an error happened while I tried to handle your update. My developer has been notified."
        update.effective_message.reply_text(text)
    # This traceback is created with accessing the traceback object from the sys.exc_info, which is returned as the
    # third value of the returned tuple. Then we use the traceback.format_tb to get the traceback as a string, which
    # for a weird reason separates the line breaks in a list, but keeps the linebreaks itself. So just joining an
    # empty string works fine.
    trace = "".join(traceback.format_tb(sys.exc_info()[2]))
    # lets try to get as much information from the telegram update as possible
    payload = ""
    # normally, we always have an user. If not, its either a channel or a poll update.
    if update.effective_user:
        payload += f' with the user {mention_html(update.effective_user.id, update.effective_user.first_name)}'
    # there are more situations when you don't get a chat
    if update.effective_chat:
        payload += f' within the chat <i>{update.effective_chat.title}</i>'
        if update.effective_chat.username:
            payload += f' (@{update.effective_chat.username})'
    # but only one where you have an empty payload by now: A poll (buuuh)
    if update.poll:
        payload += f' with the poll id {update.poll.id}.'
    # lets put this in a "well" formatted text
    text = f"Hey.\n The error <code>{context.error}</code> happened{payload}. The full traceback:\n\n<code>{trace}</code>"
    # and send it to the dev(s)
    for dev_id in devs:
        context.bot.send_message(dev_id, text, parse_mode=ParseMode.HTML)
    # we raise the error again, so the logger module catches it. If you don't use the logger module, use it.
    raise

def send_typing_action(func):
    '''decorator that sends typing action while processing func command.'''
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
        return func(update, context,  *args, **kwargs)
    return wrapped

def log(func):
    '''decorator that logs who said what to the bot'''
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        id = update.effective_user.id
        name = update.effective_user.username
        #pprint(update.to_dict())
        context.user_data['meta'] = {
            'last_talked': update.effective_message['date'],
            'user_details': update.effective_message.to_dict()['from']
        }
        logging.info(f'{name} ({id}) said:\n{update.effective_message.text}')
        return func(update, context, *args, **kwargs)
    return wrapped

def restricted(func):
    '''decorator that restricts use to only the admins listed in secrets.py'''
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        name = update.effective_user.username
        if user_id not in LIST_OF_ADMINS:
            logging.info(f'Unauthorized access: {name} ({user_id}) tried to use {func.__name__}()')
            return
        return func(update, context, *args, **kwargs)
    return wrapped


@send_typing_action
@log
def incoming(update, context):
    '''main function that deals with incoming messages that are the meat and potatos of this bot'''
    responses = main(update.effective_message.text, context)
    for response in responses:
        logging.info(f'bot said:\n{response}')
        context.bot.send_message(chat_id=update.effective_message.chat_id, text=response, parse_mode=ParseMode.HTML)

@send_typing_action
@log
def warehouse(update, context):
    '''show a summary of what parts are ready to craft'''
    responses = warehouse_crafting(context.user_data.get('warehouse', {}))
    for response in responses:
        logging.info(f'bot said:\n{response}')
        context.bot.send_message(chat_id=update.effective_message.chat_id, text=response, parse_mode=ParseMode.HTML)


@send_typing_action
@log
def start(update, context):
    '''intro function'''
    text = 'Bot primarily for helping manage your relationship with guild stock.\n'\
           '\n'\
           'See /help for more details.'

    logging.info(f'bot said:\n{text}')
    context.bot.send_message(chat_id=update.message.chat_id, text=text, parse_mode='Markdown')

@send_typing_action
@log
def mlm(update, context):
    '''get me more stamina if you want'''
    messages = ("If you're going to recruit a new player and already have enough stamina yourself, why not use my /promo code instead?\nI'm a collector and can use every extra bit of stamina.",
        'Join the Chat Wars! First MMORPG in Telegram. Use this invite link to receive 10💰 as a welcome gift:\nhttps://telegram.me/chtwrsbot?start=ad53406f0a3544689bed29057419ae15',
    )
    for message in messages:
        logging.info(f'bot said:\n{message}')
        context.bot.send_message(chat_id=update.effective_message.chat_id, text=message, parse_mode=ParseMode.HTML)

@send_typing_action
@log
def help(update, context):
    text = 'Forward messages here for the bot to act on.\n'\
           '\n'\
           'Any list of items (eg. /stock, ⚒Crafting, etc.) - Create all the /g_deposit commands to move everything to guild stock.\n'\
           'Any message with list of missing items - Create /g_withdraw command that you need to send to guild leader.\n'\
           'A message with /g_deposit commands from this bot - Create /g_withdraw command to get your stuff back out.\n'\
           '\n'\
           'Some /settings available too.\n'\
           '\n'\
           'Paste in multiple /g_withdraw commands - Create a more efficent /g_withdraw command.'

    logging.info(f'bot said:\n{text}')
    context.bot.send_message(chat_id=update.message.chat_id, text=text, parse_mode=ParseMode.HTML)

@send_typing_action
@log
def settings(update, context):
    '''direct users to the settings'''
    text = 'Use /save and/or /ignore to customize your experience.\n'\
           '\n'\
           'Add a space-separated list of IDs after the command to save or ignore. You can limit how many of an item are affected by attaching an amount to the ID with a comma. Using the command with nothing else will show you what you have stored.\n'\
           '\n'\
           'Example:\n'\
           '`/save 01 02,150 03` 👈 Save all thread, all pelt and 150 sticks. Rest of the sticks get deposited.'

    logging.info(f'bot said:\n{text}')
    context.bot.send_message(chat_id=update.message.chat_id, text=text, parse_mode='Markdown')

@send_typing_action
@log
def save(update, context):
    '''set/view the list of item ids you want to hide in the market rather than deposit'''
    setting_saver(update, context, 'save')

@send_typing_action
@log
def ignore(update, context):
    '''set/view the list of item ids you want to ignore'''
    setting_saver(update, context, 'ignore')

def setting_saver(update, context, section):
    if context.args:
        context.user_data[section] = {}
    for id in context.args:
        count = ''
        if ',' in id:
            id, count = id.split(',')
        context.user_data[section][id] = count

    settings = sorted(context.user_data.get(section, {}))
    res = [f'{"Saving" if section == "save" else "Ignoring"} {"these" if len(settings) > 1 else "this"}:']
    cmd = [f'/{section}']
    for id in settings:
        name = id_to_name.get(id, 'unknown')
        count = context.user_data[section][id]
        id_count = f'{id}{"," if count else ""}{count}'
        res.append(f' `{id_count}` {name.title()}')
        cmd.append(id_count)
    if settings:
        res.append(f'`{" ".join(cmd)}`')

    text = '\n'.join(res)
    logging.info(f'bot said:\n{text}')
    context.bot.send_message(chat_id=update.message.chat_id, text=text, parse_mode='Markdown')

@send_typing_action
@log
def ping(update, context):
    '''show signs of life'''
    text = "/pong"
    logging.info(f'bot said:\n{text}')
    context.bot.send_message(chat_id=update.message.chat_id, text=text, parse_mode='Markdown')
@send_typing_action
@log
def pong(update, context):
    '''ǝɟᴉl ɟo suƃᴉs ʍoɥs'''
    text = "/ping"
    logging.info(f'bot said:\n{text}')
    context.bot.send_message(chat_id=update.message.chat_id, text=text, parse_mode='Markdown')

@send_typing_action
@log
def now(update, context):
    '''what time is it'''
    text = datetime.utcnow().isoformat()
    logging.info(f'bot said:\n{text}')
    context.bot.send_message(chat_id=update.message.chat_id, text=text, parse_mode='Markdown')

@send_typing_action
@log
def time(update, context):
    text = emeryradio()
    logging.info(f'bot said:\n{text}')
    context.bot.send_message(chat_id=update.message.chat_id, text=text, parse_mode='Markdown')

@restricted
@log
def restart(update, context):
    def stop_and_restart():
        """Gracefully stop the Updater and replace the current process with a new one"""
        updater.stop()
        os.execl(sys.executable, sys.executable, *sys.argv)

    update.message.reply_text('Bot is restarting...')
    logging.info('Bot is restarting...')
    Thread(target=stop_and_restart).start()
    update.message.reply_text("...and we're back")
    logging.info("...and we're back")

@restricted
@log
def say(update, context):
    if context.args:
        text=' '.join(context.args[1:])
        context.bot.send_message(chat_id=context.args[0], text=text, parse_mode='Markdown')
    else:
        with open('user.persist', 'rb') as fp:
            d = pickle.load(fp)
        speakers = sorted((
                           f'{talker["meta"]["last_talked"]}, @{talker["meta"]["user_details"]["username"]}, '
                           f'{talker["meta"]["user_details"]["first_name"]} {talker["meta"]["user_details"].get("last_name", "")}\n'
                           f'<code>/say {id} </code>'
                           for id, talker in d['user_data'].items() if talker.get('meta', '')
                          ), reverse=True)[:5]
        text = '\n'.join(speakers)
        context.bot.send_message(chat_id=update.effective_message.chat_id, text=text, parse_mode=ParseMode.HTML)
    logging.info(f'bot said:\n{text}')

@restricted
@log
def clear(update, context):
    '''used to wipe parts of user_data for testing'''
    text = str(context.user_data.pop('warehouse', 'None'))
    logging.info(f'bot said:\n{text}')
    context.bot.send_message(chat_id=update.message.chat_id, text=text, parse_mode=ParseMode.HTML)


dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('mlm', mlm))
dispatcher.add_handler(CommandHandler('help', help))
dispatcher.add_handler(CommandHandler('settings', settings))
dispatcher.add_handler(CommandHandler('save', save))
dispatcher.add_handler(CommandHandler('ignore', ignore))
dispatcher.add_handler(CommandHandler('ping', ping))
dispatcher.add_handler(CommandHandler('pong', pong))
dispatcher.add_handler(CommandHandler('now', now))
dispatcher.add_handler(CommandHandler('time', time))
dispatcher.add_handler(MessageHandler(Filters.forwarded, incoming))
dispatcher.add_handler(MessageHandler(Filters.text, incoming))
dispatcher.add_handler(CommandHandler('g_withdraw', incoming))
dispatcher.add_handler(CommandHandler('warehouse', warehouse))
dispatcher.add_handler(CommandHandler('w', warehouse))
dispatcher.add_handler(CommandHandler('r', restart))#, filters=Filters.user(user_id=LIST_OF_ADMINS)))
dispatcher.add_handler(CommandHandler('say', say))#, filters=Filters.user(user_id=LIST_OF_ADMINS)))
dispatcher.add_handler(CommandHandler('clear', clear))
dispatcher.add_error_handler(error)

logging.info('bot started')
updater.start_polling()
updater.idle()

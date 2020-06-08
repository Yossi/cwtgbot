import os
import sys
import logging
import traceback
import pickle
import html
import random
from datetime import datetime
from threading import Thread
from functools import wraps
from pprint import pprint

from telegram import ParseMode
from telegram import ChatAction
from telegram.utils.helpers import mention_html
from telegram.ext import Updater, PicklePersistence
from telegram.ext import CommandHandler, MessageHandler
from telegram.ext import Filters
from timezonefinder import TimezoneFinder

from tealeyes import tealeyes
from brains import main, warehouse_crafting, withdraw_craft, deals_report
from brains import stock_list, alch_list, other_list
from brains import id_lookup
from util import warehouse_load_saved, send
from secrets import TOKEN, LIST_OF_ADMINS

logging.basicConfig(format='%(asctime)s - %(levelname)s\n%(message)s', level=logging.INFO)

persistence = PicklePersistence(filename='user.persist', on_flush=False)
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
        payload += f' within the chat <i>{html.escape(str(update.effective_chat.title))}</i>'
        if update.effective_chat.username:
            payload += f' (@{update.effective_chat.username})'
    # but only one where you have an empty payload by now: A poll (buuuh)
    if update.poll:
        payload += f' with the poll id {update.poll.id}.'
    # lets put this in a "well" formatted text
    text = f"Hey.\n The error <code>{html.escape(str(context.error))}</code> happened{payload}. The full traceback:\n\n<code>{html.escape(trace)}</code>"
    # and send it to the dev(s)
    for dev_id in devs:
        context.bot.send_message(dev_id, update.effective_message.text, parse_mode=ParseMode.HTML)
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
    if not update.effective_message.text: return
    responses = main(update, context)
    for response in responses:
        send(response, update, context)

@send_typing_action
@log
def warehouse(update, context):
    '''show a summary of what parts are ready to craft'''
    responses = warehouse_crafting(context)
    for response in responses:
        send(response, update, context)

def warehousecmd(update, context):
    context.args = update.effective_message.text.split('_')[1:]
    warehouse(update, context)

@send_typing_action
@log
def craft(update, context):
    '''create withdraw command for the stuff needed to craft this'''
    responses = withdraw_craft(context)
    for response in responses:
        send(response, update, context)

def craftcmd(update, context):
    context.args = update.effective_message.text.split('_')[1:]
    craft(update, context)

@send_typing_action
@log
def stock(update, context):
    '''show a list of parts we have in order of quantity'''
    responses = stock_list(context)
    for response in responses:
        send(response, update, context)

@send_typing_action
@log
def alch(update, context):
    '''show a list of ingredients we have in order of quantity'''
    responses = alch_list(context)
    for response in responses:
        send(response, update, context)

@send_typing_action
@log
def other(update, context):
    '''show a list of equipment we have and how much it can be instantly sold for'''
    responses = other_list(context)
    for response in responses:
        send(response, update, context)

@send_typing_action
@log
def deals(update, context):
    response = deals_report(context)
    send(response, update, context)

@send_typing_action
@log
def start(update, context):
    '''intro function'''
    text = 'Bot primarily for helping manage your relationship with guild stock.\n'\
           '\n'\
           'See /help for more details.'

    send(text, update, context)

@send_typing_action
@log
def mlm(update, context):
    '''get me more stamina if you want'''
    messages = ("If you're going to recruit a new player and already have enough stamina yourself, why not use my /promo code instead?\nI'm a collector and can use every extra bit of stamina.",
        'Join the Chat Wars! First MMORPG in Telegram. Use this invite link to receive 10💰 as a welcome gift:\nhttps://telegram.me/chtwrsbot?start=ad53406f0a3544689bed29057419ae15',
    )
    for message in messages:
        send(message, update, context)

@send_typing_action
@log
def help(update, context):
    text = 'Forward messages here for the bot to act on.\n'\
           '\n'\
           'Any list of items (eg. /stock, ⚒Crafting, etc.) - Create all the /g_deposit commands to move everything to guild stock.\n'\
           'Any message with list of missing items - Create /g_withdraw command that you need to send to guild leader.\n'\
           'A message with /g_deposit commands from this bot - Create /g_withdraw command to get your stuff back out.\n'\
           'Any message that has your guild tag in it - Record you as a member of that guild.\n'\
           'Paste in multiple /g_withdraw commands - Create a more efficent /g_withdraw command.\n'\
           '/warehouse - Show a list of things that have enough recipies & parts in guild stock to craft.\n'\
           '/stock & /alch - List guild stock of these categories in decending order of quantity.\n'\
           '\n'\
           'Some /settings available too.\n'\

    send(text, update, context)

@send_typing_action
@log
def settings(update, context):
    '''direct users to the settings'''
    text = 'Use /save and/or /ignore to customize your experience.\n'\
           '\n'\
           'Add a space-separated list of IDs after the command to save or ignore. You can limit how many of an item are affected by attaching an amount to the ID with a comma. Using the command with nothing else will show you what you have stored.\n'\
           '\n'\
           'Example:\n'\
           '<code>/save 01 02,150 03</code> 👈 Save all thread, all pelt and 150 sticks. Rest of the sticks get deposited.'

    send(text, update, context)

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
        if id_lookup.get(id, {}).get('name', False): # Don't save if item doesn't exist
            context.user_data[section][id] = count

    settings = sorted(context.user_data.get(section, {}))
    if len(settings) > 0:
        res = [f'{"Saving" if section == "save" else "Ignoring"} {"these" if len(settings) > 1 else "this"}:']
    else:
        res = [f'Not {"saving" if section == "save" else "ignoring"} anything!']
    cmd = [f'/{section}']
    for id in settings:
        name = id_lookup.get(id, {}).get('name', 'unknown')
        count = context.user_data[section][id]
        id_count = f'{id}{"," if count else ""}{count}'
        res.append(f' <code>{id_count}</code> {name}')
        cmd.append(id_count)
    if settings:
        res.append(f'<code>{" ".join(cmd)}</code>')

    text = '\n'.join(res)
    send(text, update, context)

@send_typing_action
@log
def location(update, context):
    tf = TimezoneFinder()
    latitude, longitude = update.effective_message.location.latitude, update.effective_message.location.longitude
    context.user_data['location'] = round(latitude, 3), round(longitude, 3)
    context.user_data['timezone'] = tf.timezone_at(lat=latitude, lng=longitude)
    text = f'Saving your location as {context.user_data["location"]} making your timezone be {context.user_data["timezone"]}'
    send(text, update, context)

@send_typing_action
@log
def ping(update, context):
    '''show signs of life'''
    text = "/pong"
    send(text, update, context)
@send_typing_action
@log
def pong(update, context):
    '''ǝɟᴉl ɟo suƃᴉs ʍoɥs'''
    text = "/ping"
    send(text, update, context)

@send_typing_action
@log
def now(update, context):
    '''what time is it'''
    text = datetime.utcnow().isoformat()
    send(text, update, context)

@send_typing_action
@log
def time(update, context):
    text = tealeyes(context.user_data)
    send(text, update, context)

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

@restricted
@log
def say(update, context):
    '''say things as the bot'''
    if context.args:
        text = ' '.join(context.args[1:])
        logging.info(f'bot said:\n{text}')
        context.bot.send_message(chat_id=context.args[0], text=text, parse_mode=ParseMode.HTML)
    else:
        with open('user.persist', 'rb') as fp:
            d = pickle.load(fp)
        speakers = sorted((
                           f'{talker["meta"]["last_talked"]}, [{talker.get("guild","")}] @{talker["meta"]["user_details"].get("username", "??")}, '
                           f'{talker["meta"]["user_details"]["first_name"]} {talker["meta"]["user_details"].get("last_name", "")}\n'
                           f'<code>/say {id} </code>'
                           for id, talker in d['user_data'].items() if talker.get('meta', '')
                          ), reverse=True)[:max(len(d['user_data']), 5)]
        text = '\n'.join(speakers)
        send(text, update, context)

#@restricted
@log
def user_data(update, context):
    '''see and clear user_data'''
    text = str(context.user_data)
    if context.args and context.args[0] == 'clear' and len(context.args) > 1:
        context.user_data.pop(' '.join(context.args[1:]), None)
    send(text, update, context)

@restricted
@log
def chat_data(update, context):
    '''See and clear chat_data'''
    text = str(context.chat_data)
    if context.args and context.args[0] == 'clear' and len(context.args) > 1:
        context.chat_data.pop(' '.join(context.args[1:]), None)
    send(text, update, context)

@restricted
@log
def warehouse_data(update, context):
    '''See and clear warehouse_data'''
    text = str(warehouse_load_saved())
    if context.args and context.args[0] == 'clear':
        os.remove('warehouse.dict')
    send(text, update, context)

@log
def destination(update, context):
    '''choose a location to quest next'''
    locations = '🌲🍄⛰'
    text = random.choice(locations)
    send(text, update, context)

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
dispatcher.add_handler(MessageHandler(Filters.location, location))
dispatcher.add_handler(MessageHandler(Filters.forwarded, incoming))
dispatcher.add_handler(MessageHandler(Filters.text, incoming))
dispatcher.add_handler(CommandHandler('g_withdraw', incoming))
dispatcher.add_handler(CommandHandler('g_deposit', incoming))
dispatcher.add_handler(CommandHandler('warehouse', warehouse))
dispatcher.add_handler(CommandHandler('w', warehouse))
# regex below
dispatcher.add_handler(CommandHandler('craft', craft))
dispatcher.add_handler(CommandHandler('c', craft))
# regex below
dispatcher.add_handler(CommandHandler('stock', stock))
dispatcher.add_handler(CommandHandler('alch', alch))
dispatcher.add_handler(CommandHandler('other', other))
dispatcher.add_handler(CommandHandler('deals', deals))
dispatcher.add_handler(CommandHandler('r', restart))#, filters=Filters.user(user_id=LIST_OF_ADMINS)))
dispatcher.add_handler(CommandHandler('say', say))#, filters=Filters.user(user_id=LIST_OF_ADMINS)))
dispatcher.add_handler(CommandHandler('user_data', user_data))
dispatcher.add_handler(CommandHandler('chat_data', chat_data))#, filters=Filters.user(user_id=LIST_OF_ADMINS)))
dispatcher.add_handler(CommandHandler('warehouse_data', warehouse_data))#, filters=Filters.user(user_id=LIST_OF_ADMINS)))
dispatcher.add_handler(CommandHandler('go', destination))

dispatcher.add_handler(MessageHandler(Filters.regex(r'/w.*_'), warehousecmd))
dispatcher.add_handler(MessageHandler(Filters.regex(r'/c.*_'), craftcmd))

dispatcher.add_error_handler(error)

logging.info('bot started')
updater.start_polling()
updater.idle()

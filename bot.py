import logging
import os
import pickle
import random
import sys
from datetime import datetime
from functools import wraps
from threading import Thread

from telegram import ChatAction
from telegram import ParseMode
from telegram.ext import CommandHandler, MessageHandler
from telegram.ext import Filters
from telegram.ext import Updater, PicklePersistence
from timezonefinder import TimezoneFinder

import commands
from brains import main, warehouse_crafting, deals_report
from secrets import TOKEN, LIST_OF_ADMINS
from utils import warehouse, send
from utils.wiki import id_lookup

logging.basicConfig(format='%(asctime)s - %(levelname)s\n%(message)s', level=logging.INFO)

persistence = PicklePersistence(filename='user.persist', on_flush=False)
updater = Updater(token=TOKEN, persistence=persistence, use_context=True)
dispatcher = updater.dispatcher















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
def misc(update, context):
    '''show a list of the misc stuff in guild stock. Potions and the like'''
    responses = misc_list(context)
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
    messages = (
        "If you're going to recruit a new player and already have enough stamina yourself, why not use my /promo code instead?\nI'm a collector and can use every extra bit of stamina.",
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


def clear_save(update, context):
    """clear the list of item IDs you would like to save"""
    setting_clear(update, context, 'save')


@send_typing_action
@log
def ignore(update, context):
    '''set/view the list of item ids you want to ignore'''
    setting_saver(update, context, 'ignore')


def clear_ignore(update, context):
    """clear the list of item IDs you would like to ignore"""
    setting_clear(update, context, 'ignore')


def setting_saver(update, context, section):
    if context.args:
        context.user_data[section] = {}
    for id in context.args:
        count = ''
        if ',' in id:
            id, count = id.split(',')
        if id_lookup.get(id, {}).get('name', False):  # Don't save if item doesn't exist
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


def setting_clear(update, context, section):
    old_settings = []
    for item, count in sorted(context.user_data.get(section, {}).items()):
        if count:
            old_settings.append(f'{item},{count}')
        else:
            old_settings.append(item)

    previous = f'\n Previously <code>/{section} {" ".join(old_settings)}</code>' if old_settings else ''
    send(f'Ok, your {section} settings have been cleared{previous}', update, context)
    context.user_data[section] = {}


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
dispatcher.add_handler(CommandHandler('clear_save', clear_save))
dispatcher.add_handler(CommandHandler('ignore', ignore))
dispatcher.add_handler(CommandHandler('clear_ignore', clear_ignore))
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
dispatcher.add_handler(CommandHandler('misc', misc))
dispatcher.add_handler(CommandHandler('deals', deals))
dispatcher.add_handler(CommandHandler('r', restart))  # , filters=Filters.user(user_id=LIST_OF_ADMINS)))
dispatcher.add_handler(CommandHandler('say', say))  # , filters=Filters.user(user_id=LIST_OF_ADMINS)))
dispatcher.add_handler(CommandHandler('user_data', user_data))
dispatcher.add_handler(CommandHandler('chat_data', chat_data))  # , filters=Filters.user(user_id=LIST_OF_ADMINS)))
dispatcher.add_handler(CommandHandler('warehouse_data', warehouse_data))  # , filters=Filters.user(user_id=LIST_OF_ADMINS)))
dispatcher.add_handler(CommandHandler('go', destination))

dispatcher.add_handler(MessageHandler(Filters.regex(r'/w.*_'), warehousecmd))
dispatcher.add_handler(MessageHandler(Filters.regex(r'/c.*_'), craftcmd))

dispatcher.add_error_handler(commands.error)

logging.info('bot started')
updater.start_polling()
updater.idle()

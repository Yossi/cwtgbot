import logging
import pickle

from telegram import ParseMode

from utils import send
from .decorators import restricted, log


@restricted
@log
def say(update, context):
    """say things as the bot"""
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

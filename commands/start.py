from utils import send
from .decorators import log, send_typing_action


@send_typing_action
@log
def start(update, context):
    """intro function"""
    text = 'Bot primarily for helping manage your relationship with guild stock.\n'\
           '\n'\
           'See /help for more details.'
    send(text, update, context)

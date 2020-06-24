from utils import send
from .decorators import log, send_typing_action


@send_typing_action
@log
def ping(update, context):
    """show signs of life"""
    text = "/pong"
    send(text, update, context)

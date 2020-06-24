from utils import send
from utils.timewiz import timewiz
from .decorators import log, send_typing_action


@send_typing_action
@log
def time(update, context):
    text = timewiz(context.user_data)
    send(text, update, context)

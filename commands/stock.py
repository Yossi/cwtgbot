from brains import list
from utils import send
from .decorators import log, send_typing_action


@send_typing_action
@log
def stock(update, context):
    """show a list of parts we have in order of quantity"""
    responses = list.stock(context)
    for response in responses:
        send(response, update, context)

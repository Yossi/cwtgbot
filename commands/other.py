from utils import send
from .decorators import log, send_typing_action
from brains import list


@send_typing_action
@log
def other(update, context):
    """show a list of equipment we have and how much it can be instantly sold for"""
    responses = list.other(context)
    for response in responses:
        send(response, update, context)

from brains import list
from utils import send
from .decorators import send_typing_action, log


@send_typing_action
@log
def alch(update, context):
    """show a list of ingredients we have in order of quantity"""
    responses = list.alch(context)
    for response in responses:
        send(response, update, context)

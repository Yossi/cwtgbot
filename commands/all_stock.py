from brains import list
from utils import send
from .decorators import send_typing_action, log


@send_typing_action
@log
def all_stock(update, context):
    """show a list of all items we have in guild stock ordered by weight"""
    responses = list.all_stock(context)
    for response in responses:
        send(response, update, context)
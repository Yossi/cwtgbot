from .decorators import send_typing_action
from .decorators import log
from brains import warehouse_crafting
from utils import send


@send_typing_action
@log
def warehouse(update, context):
    """show a summary of what parts are ready to craft"""
    responses = warehouse_crafting(context)
    for response in responses:
        send(response, update, context)

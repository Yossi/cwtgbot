from commands.decorators import send_typing_action, log
from utils import send
from brains import list


@send_typing_action
@log
def misc(update, context):
    """show a list of the misc stuff in guild stock. Potions and the like"""
    responses = list.misc(context)
    for response in responses:
        send(response, update, context)

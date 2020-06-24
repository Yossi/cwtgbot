from brains import warehouse_crafting
from utils import send
from .decorators import log
from .decorators import send_typing_action


@send_typing_action
@log
def warehouse(update, context):
    """show a summary of what parts are ready to craft"""
    responses = warehouse_crafting(context)
    for response in responses:
        send(response, update, context)


def warehousecmd(update, context):
    context.args = update.effective_message.text.split('_')[1:]
    warehouse(update, context)

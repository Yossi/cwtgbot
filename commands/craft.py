from brains import withdraw
from utils import send
from .decorators import log, send_typing_action


@send_typing_action
@log
def craft(update, context):
    """create withdraw command for the stuff needed to craft this"""
    responses = withdraw.craft(context)
    for response in responses:
        send(response, update, context)


def craftcmd(update, context):
    context.args = update.effective_message.text.split('_')[1:]
    craft(update, context)

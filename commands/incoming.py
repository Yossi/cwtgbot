from brains import main
from utils import send
from .decorators import log
from .decorators import send_typing_action


@send_typing_action
@log
def incoming(update, context):
    """main function that deals with incoming messages that are the meat and potatos of this bot"""
    if not update.effective_message.text:
        return
    responses = main(update, context)
    for response in responses:
        send(response, update, context)

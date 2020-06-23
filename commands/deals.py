from brains import deals_report
from utils import send
from .decorators import log, send_typing_action


@send_typing_action
@log
def deals(update, context):
    response = deals_report(context)
    send(response, update, context)

from brains import prices_report
from utils import send
from .decorators import log, send_typing_action


@send_typing_action
@log
def prices(update, context):
    response = prices_report(context)
    send(response, update, context)

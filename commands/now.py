from datetime import datetime

from utils import send
from .decorators import log, send_typing_action


@send_typing_action
@log
def now(update, context):
    """what time is it"""
    text = datetime.utcnow().isoformat()
    send(text, update, context)
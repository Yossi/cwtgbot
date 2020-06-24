from utils import send
from .decorators import log, send_typing_action


@send_typing_action
@log
def pong(update, context):
    """ǝɟᴉl ɟo suƃᴉs ʍoɥs"""
    text = "/ping"
    send(text, update, context)

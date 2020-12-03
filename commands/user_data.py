import html
from utils import send
from .decorators import log


@log
def user_data(update, context):
    """see and clear user_data"""
    text = html.escape(str(context.user_data))
    if context.args and context.args[0] == 'clear' and len(context.args) > 1:
        context.user_data.pop(' '.join(context.args[1:]), None)
    send(text, update, context)

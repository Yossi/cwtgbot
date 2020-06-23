from utils import send
from .decorators import restricted, log


@restricted
@log
def chat_data(update, context):
    """See and clear chat_data"""
    text = str(context.chat_data)
    if context.args and context.args[0] == 'clear' and len(context.args) > 1:
        context.chat_data.pop(' '.join(context.args[1:]), None)
    send(text, update, context)

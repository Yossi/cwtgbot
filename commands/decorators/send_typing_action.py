from functools import wraps

from telegram import ChatAction


def send_typing_action(func):
    """decorator that sends typing action while processing func command."""
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
        return func(update, context, *args, **kwargs)
    return wrapped

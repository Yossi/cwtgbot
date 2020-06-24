from utils import send
from .decorators import log, send_typing_action


@send_typing_action
@log
def mlm(update, context):
    """get me more stamina if you want"""
    messages = (
        "If you're going to recruit a new player and already have enough stamina yourself, why not use my /promo code instead?\nI'm a collector and can use every extra bit of stamina.",
        'Join the Chat Wars! First MMORPG in Telegram. Use this invite link to receive 10💰 as a welcome gift:\nhttps://telegram.me/chtwrsbot?start=ad53406f0a3544689bed29057419ae15',
    )
    for message in messages:
        send(message, update, context)

from utils.setting_saver import setting_saver
from .decorators import log, send_typing_action


@send_typing_action
@log
def save(update, context):
    """set/view the list of item ids you want to hide in the market rather than deposit"""
    setting_saver(update, context, 'save')

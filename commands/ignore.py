from utils.setting_saver import setting_saver

from .decorators import log, send_typing_action


@send_typing_action
@log
def ignore(update, context):
    """set/view the list of item ids you want to ignore"""
    setting_saver(update, context, 'ignore')

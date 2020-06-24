from utils.setting_clear import setting_clear


def clear_ignore(update, context):
    """clear the list of item IDs you would like to ignore"""
    setting_clear(update, context, 'ignore')

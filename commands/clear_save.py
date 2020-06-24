from utils.setting_clear import setting_clear


def clear_save(update, context):
    """clear the list of item IDs you would like to save"""
    setting_clear(update, context, 'save')

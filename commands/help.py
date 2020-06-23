from utils import send

from .decorators import log, send_typing_action


@send_typing_action
@log
def help(update, context):
    text = 'Forward messages here for the bot to act on.\n' \
           '\n' \
           'Any list of items (eg. /stock, ⚒Crafting, etc.) - Create all the /g_deposit commands to move everything to guild stock.\n' \
           'Any message with list of missing items - Create /g_withdraw command that you need to send to guild leader.\n' \
           'A message with /g_deposit commands from this bot - Create /g_withdraw command to get your stuff back out.\n' \
           'Any message that has your guild tag in it - Record you as a member of that guild.\n' \
           'Paste in multiple /g_withdraw commands - Create a more efficent /g_withdraw command.\n' \
           '/warehouse - Show a list of things that have enough recipies & parts in guild stock to craft.\n' \
           '/stock & /alch - List guild stock of these categories in decending order of quantity.\n' \
           '\n' \
           'Some /settings available too.\n'
    send(text, update, context)

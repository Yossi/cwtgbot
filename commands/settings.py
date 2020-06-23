from utils import send
from .decorators import log, send_typing_action


@send_typing_action
@log
def settings(update, context):
    """direct users to the settings"""
    text = 'Use /save and/or /ignore to customize your experience.\n'\
           '\n'\
           'Add a space-separated list of IDs after the command to save or ignore. You can limit how many of an item are affected by attaching an amount to the ID with a comma. Using the command with nothing else will show you what you have stored.\n'\
           '\n'\
           'Example:\n'\
           '<code>/save 01 02,150 03</code> 👈 Save all thread, all pelt and 150 sticks. Rest of the sticks get deposited.'
    send(text, update, context)

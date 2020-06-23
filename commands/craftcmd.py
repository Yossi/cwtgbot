from commands.craft import craft


def craftcmd(update, context):
    context.args = update.effective_message.text.split('_')[1:]
    craft(update, context)

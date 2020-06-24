from commands import warehouse


def warehousecmd(update, context):
    context.args = update.effective_message.text.split('_')[1:]
    warehouse(update, context)

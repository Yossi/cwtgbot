import commands.user_data
from utils import send


def setting_clear(update, context, section):
    old_settings = []
    for item, count in sorted(commands.user_data.user_data.get(section, {}).items()):
        if count:
            old_settings.append(f'{item},{count}')
        else:
            old_settings.append(item)

    previous = f'\n Previously <code>/{section} {" ".join(old_settings)}</code>' if old_settings else ''
    send(f'Ok, your {section} settings have been cleared{previous}', update, context)
    commands.user_data.user_data[section] = {}
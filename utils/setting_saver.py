from utils import id_lookup, send


def setting_saver(update, context, section):
    if context.args:
        context.user_data[section] = {}
    for id in context.args:
        count = ''
        if ',' in id:
            id, count = id.split(',')
        if id_lookup.get(id, {}).get('name', False):  # Don't save if item doesn't exist
            context.user_data[section][id] = count

    settings = sorted(context.user_data.get(section, {}))
    if len(settings) > 0:
        res = [f'{"Saving" if section == "save" else "Ignoring"} {"these" if len(settings) > 1 else "this"}:']
    else:
        res = [f'Not {"saving" if section == "save" else "ignoring"} anything!']
    cmd = [f'/{section}']
    for id in settings:
        name = id_lookup.get(id, {}).get('name', 'unknown')
        count = context.user_data[section][id]
        id_count = f'{id}{"," if count else ""}{count}'
        res.append(f' <code>{id_count}</code> {name}')
        cmd.append(id_count)
    if settings:
        res.append(f'<code>{" ".join(cmd)}</code>')

    text = '\n'.join(res)
    send(text, update, context)

import datetime
from utils.warehouse import load_saved
from utils.wiki import id_lookup, name_lookup


def parts(matches, guild):
    """builds withdraw commands.
       expects an iterator of dicts with one key named 'number' and the other named 'id' or 'name'"""
    warehouse = load_saved(guild)
    hours = 2.5
    now = datetime.datetime.utcnow()
    command_suffixes = set()

    matches = list(matches)
    for match in matches:
        if match.get('name'):
            match['id'] = name_lookup[match['name'].strip().lower()]['id']

        if match['id'][0].isdigit():
            if int(match['id']) <= 38:
                command_suffixes.add('res')
            else:
                command_suffixes.add('alch')
        elif match['id'][0] in 'sp':
            command_suffixes.add('misc')
        elif match['id'][0] == 'r':
            command_suffixes.add('rec')
        elif match['id'][0] == 'k':
            command_suffixes.add('parts')
        elif match['id'][0] in 'wuea':
            command_suffixes.add('other')

    notice = ''
    guild_stock = {}
    still_missing = set()
    oldest = now - now
    for suffix in command_suffixes:
        suf = warehouse.get(suffix, {})
        if suf:
            age = now - suf['timestamp']
            if age < datetime.timedelta(hours=hours):
                guild_stock.update(suf['data'])
                oldest = max(oldest, age)
            else:
                still_missing.add(suffix)
        else:
            guild_stock = {}
            break

    if still_missing:
        for suffix in sorted(still_missing):
            notice += f'\n/g_stock_{suffix}'

    have = []
    missing = []
    for d in matches:
        d["number"] = d["number"] if d["number"] else "1"

        if guild_stock:
            diff = int(d["number"]) - guild_stock.get(d['id'], 0)
            if diff > 0:
                if d['id'][0] not in 'rk':
                    exchange = False
                    if id_lookup[d['id']].get('exchange', False):
                        exchange = True
                        missing.append(f"<code>/wtb_{d['id']}_{diff}</code> {id_lookup[d['id']]['name']}")
                    if id_lookup[d['id']].get('craftable', False):
                        craftcmd = f"/craft_{d['id']}_{diff} {id_lookup[d['id']]['name']}"
                        if exchange:
                            missing[-1] = missing[-1].split()[0] + f' or {craftcmd}'
                        else:
                            missing.append(craftcmd)
                else:
                    missing.append(f"<code>{d['id']} {diff}</code> {id_lookup[d['id']]['name']}")
                d['number'] = guild_stock.get(d['id'], 0)

        if d['number']:
            have.append(f' {d["id"]} {d["number"]}')

    if have:
        command = ['<code>/g_withdraw']
        for n, id in enumerate(sorted(have)):
            if not (n + 1) % 10:
                command.append('</code>\n<code>/g_withdraw')
            command.append(id)
        command.append('</code>\n\n')
        command = ''.join(command)
    else:
        command = ''

    if missing:
        missing = '\n'.join([f"Based on guild stock state {oldest.seconds // 60} minutes old, item{'' if len(missing) == 1 else 's'} missing:"] + missing + [''])
    else:
        missing = ''

    if notice:
        notice = 'Missing current guild stock state. Consider forwarding:' + notice

    return command + missing + notice


def craft(context):
    response = ["Can't craft this"]
    if context.args:
        id = context.args[0]
        info = id_lookup.get(id, {})

        count = 1
        if len(context.args) > 1:
            count = int(context.args[1])

        if info.get('craftable', False):
            recipe = [{'name': name, 'number': int(amount) * count} for name, amount in info['recipe'].items() if name != 'Gold']
            recipe_str = '\n'.join([f'   {name}: {amount}{(f" x {count} = {int(amount) * count}" if count > 1 else "")}' for name, amount in info['recipe'].items()])
            response = [
                f'<b>{info["name"]}{f" x {count}" if count > 1 else ""}</b>  /c_{id}{f"_{count}" if count > 1 else ""}\n'
                f'''   Mana requirement: {info.get("craftMana", "unknown")}💧{(f" x {count} = {info.get('craftMana', 0) * count}💧" if count > 1 else "")}\n'''
                f'{recipe_str}\n\n'
                f'{parts(recipe, context.user_data.get("guild", ""))}'
            ]

    return response

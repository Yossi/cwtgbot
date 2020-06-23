import datetime
from utils.warehouse import load_saved
from utils.wiki import id_lookup, name_lookup


def withdraw_parts(matches, guild):
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

    command = ['<code>/g_withdraw']
    have = []
    missing = []
    for d in matches:
        d["number"] = d["number"] if d["number"] else "1"

        if guild_stock:
            diff = int(d["number"]) - guild_stock.get(d['id'], 0)
            if diff > 0:
                if d['id'][0] not in 'rk':
                    exchange = False
                    if id_lookup[d['id']]['exchange']:
                        exchange = True
                        missing.append(f"<code>/wtb_{d['id']}_{diff}</code> {id_lookup[d['id']]['name']}")
                    if id_lookup[d['id']]['craftable']:
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
        for n, id in enumerate(have):
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

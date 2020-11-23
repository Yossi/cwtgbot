import pickle
import re
from collections import defaultdict
import datetime
import pytz
from brains.withdraw import parts as withdraw_parts
from utils.timewiz import is_witching_hour
from utils.wiki import id_lookup, name_lookup
from utils.warehouse import load_saved


def main(update, context, testing=False):
    """returns a list of strings that are then each sent as a separate message"""
    text = update.effective_message.text
    ret = []

    def storage(m):
        """handles /stock output"""
        percent_full = 100 * int(m[1]) / int(m[2])
        ret.append(f'{percent_full}% full')
        items = text.split('\n')[1:]
        if items[0].startswith('Use /sg_{code} to trade some amount of resource for '):
            items = (''.join(item.partition(' ')[::-1]) for item in items[2:])
        generic(items)

    def more(items):
        """handles /more output"""
        def tidy(items):
            for item in items[1:]:
                slash, _ = item.partition(' ')[::2]
                name, count = _.partition(' x ')[::2]
                yield f'{name} ({count}) {slash}'
        generic(tidy(items))

    def generic(items):
        """does most of the work sorting a list of items into /wts and /g_deposit buckets.
           expects an iterator of strings in the form ['<Item Name> (<Item Count>)']"""
        sales = []
        deposits = []
        for item in items:
            match = re.search(r'(.+)\((\d+)\)( \/.+_(.+))?', item)
            if not match:
                continue
            name = match[1].strip()
            if 'murky' in name:
                continue  # TODO: if murkies ever make it into the wiki, remove this condition
            name = name.replace('📃', '').replace('🏷', '').replace('🧩','')
            if name[0] == '⚡':
                name = name.partition(' ')[2]
            id = name_lookup.get(name.lower(), {}).get('id')
            if not id and '_' in name:
                id = item.strip().rpartition('_')[2]
            if id not in id_lookup:
                continue
            if not id_lookup[id]['depositable']:
                continue
            count_total = int(match[2])
            if match[4]:
                id = match[4].strip()
            if id in context.user_data.get('save', {}):
                max_weight = 1000 // id_lookup[id]['weight']
                count_keep = context.user_data['save'][id]
                if not count_keep:
                    count_keep = count_total
                count_keep = min(int(count_keep), count_total)
                count_deposit = count_total - count_keep
                while count_keep > max_weight:
                    sales.append(f'/wts_{id}_{max_weight}_2500')
                    count_keep = count_keep - max_weight
                sales.append(f'/wts_{id}_{count_keep}_2500 {name}')
                if count_deposit:
                    deposits.append(f'/g_deposit_{id}{"_"+str(count_deposit) if count_deposit != 1 else ""} {name}')
            elif id in context.user_data.get('ignore', {}):
                count_keep = context.user_data['ignore'][id]
                if not count_keep:
                    count_keep = count_total
                count_keep = min(int(count_keep), count_total)
                count_deposit = count_total - count_keep
                if count_deposit:
                    deposits.append(f'/g_deposit_{id}{"_"+str(count_deposit) if count_deposit != 1 else ""} {name}')
            else:
                deposits.append(f'/g_deposit_{id}{"_"+str(count_total) if count_total != 1 else ""} {name}')

        if sales:
            if len(sales) == 1:
                sales = sales[0].split()[0] # trims the name off the end
            else:
                sales = '\n'.join(sorted(sales))

            if is_witching_hour():
                matches = re.finditer(r'\/wts_(?P<id>\d+)_(?P<number>\d+)_2500(?P<name>.+)?', sales)
                fire_sale = ['Market is closed so you get deposit commands.\nForward this message back to the bot after battle to get the withdraw commands for a refund.\n']
                for match in matches:
                    d = match.groupdict()
                    fire_sale.append(f'/g_deposit_{d["id"]}{"_"+d["number"] if d["number"] != "1" else ""}{d["name"] if d["name"] else ""}')
                sales = '\n'.join(sorted(fire_sale))
            ret.append(sales)

        if deposits:
            if len(deposits) == 1:
                deposits = [deposits[0].split()[0]]
            ret.append('\n'.join(sorted(deposits)))

    def withdraw():
        """process missing items messages"""
        matches = re.finditer(r'(?P<number>\d+) x (?P<name>.+)', text)
        if matches:
            ret.append(f'{text}\nRecipient shall send to guild leader/squire:\n{withdraw_parts((match.groupdict() for match in matches), context.user_data.get("guild", ""))}')

    def refund():
        """process returned /g_deposit message from ourselves"""
        matches = re.finditer(r'\/g_deposit_(?P<id>[aestchwpmkr]{0,3}\d+)(_(?P<number>\d+))?', text)
        if matches:
            ret.append(withdraw_parts((match.groupdict() for match in matches), context.user_data.get('guild', '')))

    def rerequest():
        """you asked for a withdrawal and then you wandered off to look at squirrels too long? i gotchu fam"""
        matches = list(re.finditer(r'\n(?P<name>[^⚡️+\d\v]+) x (?P<number>\d+)', text))
        response = ['Timeout expired. Please resend:']
        for match in matches:
            response.append(match.string[match.start():match.end()])
        response = "".join(response)
        ret.append(f'{response}\n{withdraw_parts((match.groupdict() for match in matches), context.user_data.get("guild", ""))}')

    def consolidate():
        """consolidate /g_withdraw commands"""
        response = []
        command = []
        count = defaultdict(int)
        matches = re.finditer(r'(?P<id>[aestchwpmkr]{0,3}\d+)\s+(?P<number>\d+)', text)
        for match in matches:
            d = match.groupdict()
            count[d['id']] += int(d['number'])
        for id, number in count.items():
            response.append(f'{id_lookup[id]["name"]} x {number}\n')
            command.append({'id': id, 'number': number})
        ret.append(f'{"".join(response)}\n{withdraw_parts(command, context.user_data.get("guild", ""))}')

    def warehouse_in():
        """read in /g_stock_* forwards"""
        def discover_id(testname):
            '''slow base_id finder for use only with troublesome custom named pieces of equipment'''
            lookup_names = [item for id, item in id_lookup.items() if id[0] in 'aw' and item.get('depositable') and item.get('enchantable')]
            result = [item['id'] for item in lookup_names if item['name'] in testname]
            if len(result) == 1:
                return result[0]
            return 'x'  # someone is trying to be difficult

        followup = {
            'res': '/stock',
            'alch': '/alch',
            'rec': '/warehouse',
            'parts': '/w_1',
            'other': '/other',
            'misc': '/misc'
        }
        guild = context.user_data.get('guild', '')
        if not hasattr(update.effective_message.forward_from, 'id') or update.effective_message.forward_from.id not in [408101137]:  # @chtwrsbot
            ret.append('Must be a forward from @chtwrsbot. Try again.')
        else:
            now = update.effective_message.forward_date
            warehouse = load_saved()
            data = {}
            for row in text.split('\n')[1:]:
                if row in '📕📗📘📙📒':
                    continue
                if row[0] == 'u':
                    row += ' x 1'
                s = row.split()
                data[s[0]] = int(s[-1])

            id_sample = list(data.keys())[0]
            if id_sample[0].isdigit():
                if int(id_sample) <= 38:
                    key = 'res'
                else:
                    key = 'alch'
            elif id_sample[0] in 'spfc':
                key = 'misc'
            elif id_sample[0] == 'r':
                key = 'rec'
            elif id_sample[0] == 'k':
                key = 'parts'
            elif id_sample[0] in 'wueat':
                key = 'other'
                data = {}
                for row in text.split('\n')[1:]:
                    if not row or row in '📕📗📘📙📒':
                        continue
                    if row[0] == 'u':
                        row += ' x 1'
                    s = row.split()
                    supplied_id = s[0]
                    count = s[-1]
                    modifier = ''
                    if s[1].startswith('⚡'):
                        modifier = s.pop(1)
                    name = ' '.join(s[1:-2])
                    base_id = name_lookup.get(name.lower(), {}).get('id')
                    if not base_id:
                        base_id = discover_id(name)  # preserve case here
                    data.setdefault(base_id, []).append((supplied_id, f'{modifier} {name}', int(count)))

            if not warehouse.get(guild):
                warehouse[guild] = {}
            if not warehouse[guild].get(key) or now > warehouse[guild][key].get('timestamp', datetime.datetime.min).replace(tzinfo=datetime.timezone.utc):
                warehouse[guild][key] = {'timestamp': now, 'data': data}
                with open('warehouse.dict', 'wb') as warehouseFile:
                    pickle.dump(warehouse, warehouseFile)
                ret.append(followup.get(key, key))
            else:
                ret.append(f'{key}, but not newer than data on file')
        if not guild:
            ret.append("Your guild affiliation is not on file with this bot. Consider forwarding something that indicates what guild you're in. Eg: /me or /report or /hero")

    def guild(matches):
        if not hasattr(update.effective_message.forward_from, 'id') or update.effective_message.forward_from.id not in [408101137]:  # @chtwrsbot  (265204902 is cw3)
            ret.append('Must be a forward from @chtwrsbot. Try again.')
        elif len(matches) != 1:
            ret.append(f'Unclear what guild you mean.\nFound: {[match.groupdict()["guild"] for match in matches]}')
        else:
            context.user_data['guild'] = matches[0].groupdict()['guild']
            ret.append(f'Recording you as a member of [{context.user_data["guild"]}] Guild')

    def inspect():
        output = []
        for match in re.finditer(r'(?P<equip_name>.+) \/.{2,3}_(?P<equip_id>.+)', text):
            match = match.groupdict()
            output.append(f'/inspect_{match["equip_id"]} {match["equip_name"]}')
            output.sort()
        ret.append('\n'.join(output))

    def advisor():
        filters = {
            'Ja': 700,
            'St': 700,
            'Sc': 0
        }
        for match in re.finditer(r'/adv_(?P<code>.{4}) (?P<name>.+), the lvl.(?P<level>\d) (?P<class>.+) 💰(?P<price>\d+)', text):
            match = match.groupdict()
            if filters[match['class'][:2]] >= int(match['price']):
                # ret.append('L<b>{level} {class}</b> {price}💰\n{name}'.format(**match))
                ret.append(f'/g_hire {match["code"]}')

    def countdown_to_datetime(matches):
        usertz_str = context.user_data.get('timezone')
        if usertz_str:
            nowdt = datetime.datetime.now(pytz.timezone(usertz_str))
        else:
            return 'To get clock times from countdown timers, please set a timezone by sending a pin located in your timezone.\nThis bot stores 3 decimal places of precision.\nSee https://xkcd.com/2170/'

        output = []
        a = 0
        for match in matches:
            b, c = match.span()
            output.append(text[a:b] + '⏰')
            a = c
            delta = datetime.timedelta(**{k:int(v) for k,v in match.groupdict().items() if v})
            template = '%H:%M'
            if nowdt.date() != (nowdt+delta).date():
                template = '%H:%M %a, %b %d'
            output.append((nowdt+delta).strftime(template))
        output.append(text[a:])
        return ''.join(output)

    storage_match = re.search(r'📦Storage \((\d+)/(\d+)\):', text)
    more_match = '📦Your stock:' in text
    generic_match = re.search(r'(.+)(?<!arrow )\((\d+)\)', text)
    withdraw_match = re.search(r'Not enough materials|Materials needed for|Not enough resources', text)
    refund_match = re.search(r'\/g_deposit_[aestchwpmkr]{0,3}\d+_(\d+)?', text)
    consolidate_match = text.startswith('/g_withdraw')
    rerequest_match = '/g_receive' in text
    warehouse_match = 'Guild Warehouse:' in text
    guild_matches = list(re.finditer(r'(?P<castle_sign>[(🐺🐉🌑🦌🥔🦅🦈)])(.?)\[(?P<guild>[A-Z\d]{2,3})\]', text))
    equipment_match = '🎽Equipment' in text
    advisor_match = 'Advisers available for hire today is:' in text
    countdown_match = list(re.finditer(r'⏰((?P<days>[\d]+?)d)?((?P<hours>[\d]+?)h)?((?P<minutes>[\d]+?)m(in)?)?$', text, flags=re.M))

    matched_regexs = { # for debugging
        'storage_match': bool(storage_match),
        'more_match': bool(more_match),
        'generic_match': bool(generic_match),
        'withdraw_match': bool(withdraw_match),
        'refund_match': bool(refund_match),
        'consolidate_match': bool(consolidate_match),
        'rerequest_match': bool(rerequest_match),
        'warehouse_match': bool(warehouse_match),
        'guild_matches': bool(guild_matches),
        'equipment_match': bool(equipment_match),
        'advisor_match': bool(advisor_match),
        'countdown_match': bool(countdown_match),
    }
    # print(matched_regexs)

    if storage_match:
        storage(storage_match)
    elif more_match:
        more(text.split('\n'))
    elif generic_match:
        generic(text.split('\n'))
    elif withdraw_match:
        withdraw()
    elif refund_match:
        refund()
    elif consolidate_match:
        consolidate()
    elif rerequest_match:
        rerequest()
    elif warehouse_match:
        warehouse_in()
    elif guild_matches:
        guild(guild_matches)
    elif equipment_match:
        inspect()
    elif advisor_match:
        advisor()
    else:
        ret.append('')

    if countdown_match:
        ret.append(countdown_to_datetime(countdown_match))

    if testing:
        return ret, matched_regexs
    return ret

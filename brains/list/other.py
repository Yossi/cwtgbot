import datetime
import io
import re

import matplotlib.pyplot as plt

from utils.warehouse import load_saved
from utils.wiki import id_lookup


def other(context):
    warehouse = load_saved(guild=context.user_data.get('guild', ''))
    hours = 3
    responses = []
    now = datetime.datetime.utcnow()
    if (other := warehouse.get('other', {})) and (age := now - other['timestamp']) < datetime.timedelta(hours=hours):
        output = [f'Based on /g_stock_other data {age.seconds // 60} minutes old:\n']
        page_counter = 0
        value_to_weight = {id: id_lookup.get(id, {}).get('shopSellPrice', 0)/id_lookup.get(id, {}).get('weight', 1) for id in other['data']}
        for id in sorted(value_to_weight, key=value_to_weight.get, reverse=True):
            items = other['data'][id]
            hold_output = []
            sub_output = []
            item_count = 0
            for item in sorted(items):
                item_id, name, count = item
                if item_id.startswith('u') and (match := re.search(r'[ˢᵃᵇᶜᵈᵉ]+', item_id)):
                    split = match.span()[0]
                    item_id = item_id[:split] + '​' + item_id[split:]  # zero width space
                item_count += count
                sub_output.append(f'<code>  </code>/g_i_{item_id} {name} x {count}')
            hold_output.append(f"<code>{id}</code> {id_lookup.get(id, {}).get('name', 'Assorted')} ∑ {item_count} 💰{id_lookup.get(id, {}).get('shopSellPrice', '??')}")
            hold_output.append(f"💰/⚖️ {value_to_weight[id]:.2f}")
            hold_output.extend(sub_output)
            hold_output.append(' ')
            hold_output = '\n'.join(hold_output)

            page_counter += len(hold_output.encode('utf-8'))
            if page_counter >= 3000:  # tg officially supports messages as long as 4096, but the formatting gives up around 3000
                responses.append('\n'.join(output))
                page_counter = 0
                output = []
            output.append(hold_output)

        count_and_weight = {id: sum(list(zip(*other['data'][id]))[2]) * id_lookup.get(id, {}).get('weight', 0) for id in other['data']}
        sort_by_weight = sorted(count_and_weight, key=count_and_weight.get, reverse=True)
        x = [count_and_weight[id] for id in sort_by_weight]
        y = [f"{id_lookup.get(id, {'name': 'assorted'})['name'].lower()} {id}" for id in sort_by_weight]
        r = range(len(x))
        plt.clf()  # clear plot, because it doesn't get cleared from last run
        plt.figure(figsize=(6.4, 1.5+(len(sort_by_weight)*0.15)))
        plt.barh(r, x)
        plt.yticks(r, y, fontsize='8')
        plt.legend(loc='upper right', labels=['Other by Weight'])
        plt.subplots_adjust(left=0.3)
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)

        responses.append('\n'.join(output))

        responses.append(buf)
    else:
        responses.append(f'Missing recent guild stock state (&lt; {hours} hours old). Please forward the output from /g_stock_other and try again')
    return responses

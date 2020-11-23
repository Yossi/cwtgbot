import datetime
import io
import pickle
import re

import matplotlib.pyplot as plt

from utils import get_id_location
from utils.warehouse import load_saved
from utils.wiki import id_lookup, name_lookup


def warehouse_crafting(context):
    warehouse = load_saved(guild=context.user_data.get('guild', ''))
    hours = 2.5
    responses = []
    now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
    if (rec := warehouse.get('rec', {})) and (parts := warehouse.get('parts', {})) and \
            (age_rec := now - rec['timestamp']) < datetime.timedelta(hours=hours) and \
            (age_parts := now - parts['timestamp']) < datetime.timedelta(hours=hours):
        try:
            with open('auctionprices.dict', 'rb') as fp:
                prices = pickle.load(fp)
        except FileNotFoundError:
            prices = {}

        older_command = '/g_stock_parts' if age_parts >= age_rec else '/g_stock_rec'
        output = [f'Based on {older_command} data {max(age_rec, age_parts).seconds // 60} minutes old:\n']
        page_counter = 0
        for n in range(1, 125):
            if 62 <= n <= 77:
                continue

            rec_id = f'r{n:02}'
            name = id_lookup[rec_id]['name'].rpartition(" ")[0]
            recipe = name_lookup.get(name.lower(), {}).get('recipe', {})
            parts_needed, part_name = '1000000', 'Part'
            for k in recipe:
                if k.startswith(name.split()[0]) and not k.endswith('Recipe'):
                    parts_needed = int(recipe.get(k))
                    part_name = k.rpartition(' ')[2]
                    part_id = name_lookup.get(k.lower(), {}).get('id')

            count_recipes = rec['data'].get(rec_id, 0)
            count_parts = parts['data'].get(part_id, 0)
            complete_parts_sets = count_parts // parts_needed
            # parts_missing_for_next_set = count_parts % parts_needed
            # recipes_missing = complete_parts_sets - count_recipes
            things_missing = int(not bool(count_recipes)) + max(parts_needed - count_parts, 0)
            num_craftable = min(count_recipes, complete_parts_sets)
            ready = '✅' if num_craftable else '❌'
            finished_part_id = name_lookup[name.lower()]['id']
            recipe_location = get_id_location(rec_id)
            part_location = get_id_location(part_id)
            recipe_price = ''
            part_price = ''
            if prices:
                recipe_price = str(prices.get(rec_id, ''))
                part_price = str(prices.get(part_id, ''))
                if recipe_price:
                    recipe_price = f'👝{recipe_price}'
                if part_price:
                    part_price = f'👝{part_price}'

            # Getting through this gauntlet without hitting a continue means you get displayed
            if not num_craftable and not context.args:
                continue
            if context.args and context.args[0].lower() != 'all':  # if it's 'all' then jump to after the gauntlet
                if context.args[0].isdigit() and 0 < things_missing <= int(context.args[0]):
                    pass
                elif context.args[0].lower().startswith('overstock'):
                    try:
                        multiple = int(context.args[1])
                    except IndexError:
                        multiple = 2
                    if count_parts / parts_needed <= multiple and count_recipes <= multiple:
                        continue
                else:
                    try:
                        regex = re.compile(context.args[0].lower())
                        matches = regex.findall(name.lower())
                        if not matches:
                            continue
                    except re.error:
                        continue

            hold = []
            hold.append(f'{ready} {name} /c_{finished_part_id}')
            if num_craftable:
                hold.append(f'Complete sets: <code>{num_craftable}</code>')
            hold.append(f'{part_name}s per recipe: <code>{parts_needed}</code>')
            hold.append(f'<code>{rec_id}</code> Recipe{"s" if count_recipes != 1 else ""}: <code>{count_recipes}</code> {recipe_price} {recipe_location}')
            hold.append(f'<code>{part_id}</code> {part_name}{"s" if count_parts != 1 else ""}: <code>{count_parts}</code> {part_price} {part_location}')
            hold.append(' ')
            hold = '\n'.join(hold)

            page_counter += len(hold.encode('utf-8'))
            if page_counter >= 2500:  # tg officially supports messages as long as 4096, but the formatting gives up around 3000
                responses.append('\n'.join(output))
                page_counter = 0
                output = []
            output.append(hold)

        result = '\n'.join(output)
        if result:
            responses.append(result)
        if result.rstrip().endswith(':'):
            responses.append('No matches in stock')

        if context.args and context.args[0].lower() in ('all', 'chart'):
            parts_rec = {**parts['data'], **rec['data']}
            count_and_weight = {id: parts_rec[id] * id_lookup[id]['weight'] for id in parts_rec}
            sort_by_weight = sorted(count_and_weight, key=count_and_weight.get, reverse=True)
            x = [
                [count_and_weight[id] if id[0] == 'k' else 0 for id in sort_by_weight],
                [count_and_weight[id] if id[0] == 'r' else 0 for id in sort_by_weight]
            ]
            y = [f"{id_lookup[id]['name'].lower()} {id}" for id in sort_by_weight]
            r = range(len(sort_by_weight))
            plt.clf()  # clear plot, because it doesn't get cleared from last run
            plt.figure(figsize=(6.4, 1.5+(len(sort_by_weight)*0.15)))
            plt.barh(r, x[0])
            plt.barh(r, x[1], color='red')
            plt.yticks(r, y, fontsize='8')
            plt.legend(loc='upper right', labels=['Parts', 'Recipes'])
            plt.subplots_adjust(left=0.3)
            buf = io.BytesIO()
            buf.name = 'weights.pdf'
            plt.savefig(buf, format='pdf')
            buf.seek(0)
            responses.append(buf)

    else:
        responses.append(f'Missing recent guild stock state (&lt; {hours} hours old). Please forward the output from /g_stock_parts and /g_stock_rec and try again')
    return responses

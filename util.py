import pickle
import json
import logging
from datetime import datetime, timezone

import filetype
import requests
from telegram import ParseMode

from tealeyes import CW_OFFSET, CW_PERIODS, SPEED










def game_phase():
    adjustment = -37.0
    utcdt = datetime.now(timezone.utc)
    cwtdt = datetime.fromtimestamp(SPEED * (utcdt.timestamp() + CW_OFFSET), tz=timezone.utc)
    cwadt = datetime.fromtimestamp(cwtdt.timestamp() + SPEED * adjustment, tz=timezone.utc)
    return f'{CW_PERIODS[cwadt.hour//6]}'


def get_id_location(id):
    info = id_lookup.get(id, {})
    locations = (
        ('Forest', '🌲'),
        ('Swamp', '🍄'),
        ('Valley', '⛰')
    )
    phase = game_phase()
    output = ''
    for place, emoji in locations:
        if info.get(f'drop{place}{phase}'):
            output += emoji
    if output:
        output += ' ' + get_qualifications(id)
    return output


def get_qualifications(id):
    levels = {
        22: '22≤🏅≤39',
        32: '32≤🏅≤39',
        40: '40≤🏅≤45',
        46: '46≤🏅'  # further research will inform this dict
    }
    level = levels.get(id_lookup.get(id, {}).get('questMinLevel'), '')
    roman = ['', '<code>I/II</code>', '<code>II</code>', '<code>III</code>', '<code>IV</code>', '<code>≥V</code>', '<code>VI</code>']
    perception_level = roman[id_lookup.get(id, {}).get('questPerceptionLevel', 0)]
    if perception_level:
        perception_level = '👀' + perception_level

    return level + perception_level


def warehouse_load_saved(guild='full'):
    try:
        with open('warehouse.dict', 'rb') as warehouseFile:
            if guild == 'full':
                return pickle.load(warehouseFile)
            return pickle.load(warehouseFile).get(guild, {})

    except IOError:
        return {}  # Ignore if warehouse.dict doesn't exist or can't be opened.




if __name__ == '__main__':
    from pprint import pprint
    with open('data.json', 'w') as fp:
        scrape_data(fp)
else:
    id_lookup, name_lookup = get_lookup_dicts()

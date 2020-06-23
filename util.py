import pickle
import json
import logging
from datetime import datetime, timezone

import filetype
import requests
from telegram import ParseMode

from tealeyes import CW_OFFSET, CW_PERIODS, SPEED















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
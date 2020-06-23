import datetime
import io
import os
import pickle
import re
from collections import defaultdict
from pprint import pprint
from rich import print


from util import is_witching_hour, warehouse_load_saved, get_id_location
from util import id_lookup, name_lookup




















if __name__ == '__main__':
    class Mock:
        pass
    c = Mock()
    c.user_data = {'save': {'01': '', '02': '', '08': '10'}, 'guild': 'USA'}
    c.args = ['all']

    pprint(warehouse_crafting(c))

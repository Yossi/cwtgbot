#!/usr/bin/env python
# from https://gist.github.com/Bibo-Joshi/5fd32dde338fba474fb15f40909c92f8

"""
This script prepares the file(s) saved by PicklePersistence for v13.0. How you do it:

1. Edit the PicklePersistence according to your settings below.
2. Run this script *before* upgrading to v13
3. Upgrade to v13 and run your bot to make sure everything is working

WARNING: Save a backup of your pickle file(s) before running this!
"""

from collections import defaultdict
from copy import copy

from telegram import Bot
from telegram.ext import PicklePersistence

"""
Instantiate your persistence with the same parameters as in your bot script!
"""
persistence = PicklePersistence('user.persist')


# Don't touch anything below this line!
# -------------------------------------------------------------------------------------------------
def replace_bot(obj):
    if isinstance(obj, Bot):
        return 'bot_instance_replaced_by_ptb_persistence'
    if isinstance(obj, (list, tuple, set, frozenset)):
        return obj.__class__(replace_bot(item) for item in obj)

    new_obj = copy(obj)
    if isinstance(obj, (dict, defaultdict)):
        new_obj.clear()
        for k, v in obj.items():
            new_obj[replace_bot(k)] = replace_bot(v)
        return new_obj
    if hasattr(obj, '__dict__'):
        for attr_name, attr in new_obj.__dict__.items():
            setattr(new_obj, attr_name, replace_bot(attr))
        return new_obj
    if hasattr(obj, '__slots__'):
        for attr_name in new_obj.__slots__:
            setattr(new_obj, attr_name,
                    replace_bot(replace_bot(getattr(new_obj, attr_name))))
        return new_obj

    return obj


print('Loading data.')
if persistence.single_file:
    persistence.load_singlefile()
else:
    for data in ['bot', 'chat', 'user']:
        persistence.load_file('{}_{}_data'.format(persistence.filename, data))
print('Done.')

print('Converting data.')
persistence.bot_data = replace_bot(persistence.bot_data)
persistence.chat_data = replace_bot(persistence.chat_data)
persistence.user_data = replace_bot(persistence.user_data)
print('Done.')

print('Writing to file.')
persistence.flush()
print('Done. Upgrade to v13 now and run your bot to make sure everything works.')

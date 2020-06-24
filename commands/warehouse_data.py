import os

from utils import send, warehouse
from .decorators import restricted, log


@restricted
@log
def warehouse_data(update, context):
    """See and clear warehouse_data"""
    text = str(warehouse.load_saved())
    if context.args and context.args[0] == 'clear':
        os.remove('warehouse.dict')
    send(text, update, context)

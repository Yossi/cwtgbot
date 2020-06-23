import random

from utils import send
from .decorators import log


@log
def destination(update, context):
    """choose a location to quest next"""
    locations = '🌲🍄⛰'
    text = random.choice(locations)
    send(text, update, context)

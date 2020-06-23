from .wiki import id_lookup
from .get_qualifications import get_qualifications
from .timewiz import game_phase


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

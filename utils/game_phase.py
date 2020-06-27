from datetime import datetime, timezone

def game_phase():
    utcdt = datetime.now(timezone.utc)
    return game_time(utcdt)

def game_time(datetime):
    game_time_lookup = [
                   'morning', 'day', 'day', 'evening', 'evening', 'night', 'night',
        'morning', 'morning', 'day', 'day', 'evening', 'evening', 'night', 'night',
        'morning', 'morning', 'day', 'day', 'evening', 'evening', 'night', 'night',
        'morning'
    ]
    return game_time_lookup[datetime.hour].title()
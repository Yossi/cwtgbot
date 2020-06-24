from datetime import datetime, time


def is_witching_hour():
    """return True if market is closed"""
    closed_times = (
        (time(6, 52), time(7, 00)),
        (time(14, 52), time(15, 00)),
        (time(22, 52), time(23, 00))
    )
    now = datetime.utcnow().time()
    return any((start < now < end for start, end in closed_times))

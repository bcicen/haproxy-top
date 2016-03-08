from datetime import datetime

def format_bytes(b):
    b = float(b)
    if b < 1000:
        return '%i' % b + ' B'
    elif 1000 <= b < 1000000:
        return '%.1f' % float(b/1000) + ' kB'
    elif 1000000 <= b < 1000000000:
        return '%.1f' % float(b/1000000) + ' mB'
    elif 1000000000 <= b < 1000000000000:
        return '%.1f' % float(b/1000000000) + ' gB'
    elif 1000000000000 <= b:
        return '%.1f' % float(b/1000000000000) + ' tB'

def unix_time(dt):
    epoch = datetime.utcfromtimestamp(0)
    delta = dt - epoch
    return int(round(delta.total_seconds()))

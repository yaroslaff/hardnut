import datetime

def shortdate(dt=None):
    dt = dt or datetime.datetime.now() 
    return dt.strftime("%Y/%m/%d %H:%M:%S") 

def timesuffix(t: str):

    size = {
        'd': 86400,
        'h': 3600,
        'm': 60,
        's': 1
    }

    if not t:
        return 0

    try:
        m = size[t[-1]] # get multiplier
        return int(t[:-1]) * m
    except KeyError:
        return int(t)

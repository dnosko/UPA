import requests
from download.constants import PORTAL_ROOT

def download():
    months = range(1, 13)
    # fetch each month from the current year
    req = None
    for month in months:
        if month == 12:
            req = requests.get(PORTAL_ROOT + "2021-" + str(month))
        else:
            req = requests.get(PORTAL_ROOT + "2022-" + str(month))
        print(req.content)
        print("AAAA\n")
    return
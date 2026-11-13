import config
from datetime import datetime
def proverit_ip(ip):
    if not ip:
        return False
    chasti = ip.split('.')
    if len(chasti) != 4:
        return False
    for ch in chasti:
        try:
            chislo = int(ch)
            if chislo < 0 or chislo > 255:
                return False
        except ValueError:
            return False
    return True

def razobrat_vremya(stroka):
    if not stroka:
        return None
    try:
        return datetime.strptime(stroka, "%Y-%m-%d %H:%M:%S")
    except:
        return None

def proverit_uroven(lvl):
    return lvl in config.VALID_LEVELS
import os
import time
import config

def ensure_dirs():
    if not os.path.exists(config.DATA_DIR):
        os.makedirs(config.DATA_DIR)
    if not os.path.exists(config.LOGS_DIR):
        os.makedirs(config.LOGS_DIR)
    if not os.path.exists(config.REPORTS_DIR):
        os.makedirs(config.REPORTS_DIR)

def timer(func):
    def obertka(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"Функция {func.__name__} работала {end - start:.3f} сек")
        return result
    return obertka

def vvesti_chislo(podskazka):
    stroka = input(podskazka).strip()
    if not stroka:
        return None
    try:
        return int(stroka)
    except ValueError:
        print("Это не число!")
        return None

def vvesti_datu(podskazka):
    from datetime import datetime
    stroka = input(podskazka).strip()
    if not stroka:
        return None
    try:
        return datetime.strptime(stroka, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        print("Ошибка: нужен формат ГГГГ-ММ-ДД ЧЧ:ММ:СС")
        return None
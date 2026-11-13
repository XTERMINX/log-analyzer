import json
import os
import config

def primenit_filtry(zapisi, time_from=None, time_to=None, urovni=None, ip=None, source=None, keyword=None):
    result = []
    for zap in zapisi:
        if time_from and zap.time < time_from:
            continue
        if time_to and zap.time > time_to:
            continue
        if urovni and zap.level not in urovni:
            continue
        if ip and zap.ip != ip:
            continue
        if source and zap.source != source:
            continue
        if keyword:
            if keyword.lower() not in zap.message.lower():
                continue
        result.append(zap)
    return result

def sortirovka(zapisi, sort_by=None):
    if sort_by == "time":
        zapisi.sort(key=lambda z: z.time)
    elif sort_by == "level":
        poryadok = {"DEBUG": 1, "INFO": 2, "WARNING": 3, "ERROR": 4, "CRITICAL": 5}
        zapisi.sort(key=lambda z: poryadok.get(z.level, 0))
    return zapisi

def limit(zapisi, kolvo):
    if kolvo and kolvo > 0:
        return zapisi[:kolvo]
    return zapisi

def save_preset(imya, params):
    put = config.PRESETS_FILE
    os.makedirs(os.path.dirname(put), exist_ok=True)
    presets = {}
    if os.path.exists(put):
        with open(put, "r", encoding="utf-8") as f:
            presets = json.load(f)
    p = dict(params)
    if p.get("time_from"): p["time_from"] = p["time_from"].strftime("%Y-%m-%d %H:%M:%S")
    if p.get("time_to"): p["time_to"] = p["time_to"].strftime("%Y-%m-%d %H:%M:%S")
    presets[imya] = p
    with open(put, "w", encoding="utf-8") as f:
        json.dump(presets, f, ensure_ascii=False, indent=4)
    print("Пресет сохранен:", imya)

def load_preset(imya):
    put = config.PRESETS_FILE
    if not os.path.exists(put):
        return None
    with open(put, "r", encoding="utf-8") as f:
        presets = json.load(f)
    if imya in presets:
        return presets[imya]
    else:
        print("Нет такого пресета")
        return None
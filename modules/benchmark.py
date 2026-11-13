import time
import os
import json
import hashlib
import config
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from modules.importer import Importer

def obrabotat_odin_fail(put):
    imp = Importer()
    schetchik = 0
    for zap in imp.zagruzka_faila(put):
        schetchik += 1
    return schetchik

def posledovatelnost(puti):
    nachalo = time.time()
    vsego = 0
    for put in puti:
        vsego += obrabotat_odin_fail(put)
    konec = time.time()
    return konec - nachalo, vsego

def potoki(puti, kol_potokov=config.THREAD_COUNT):
    nachalo = time.time()
    vsego = 0
    with ThreadPoolExecutor(max_workers=kol_potokov) as executor:
        results = executor.map(obrabotat_odin_fail, puti)
        for res in results:
            vsego += res
    konec = time.time()
    return konec - nachalo, vsego

def hash_odnoy_chasti(zapisi):
    itog = 0
    for z in zapisi:
        s = f"{z.time}|{z.level}|{z.source}|{z.message}"
        h = s
        for _ in range(50):
            h = hashlib.sha256(h.encode("utf-8")).hexdigest()
        itog += int(h[:8], 16)
    return itog

def razbit_na_chasti(spisok, kol_chastey):
    razmer = max(1, len(spisok) // kol_chastey)
    return [spisok[i:i + razmer] for i in range(0, len(spisok), kol_chastey)]

def cpu_posledovatelno(zapisi):
    nachalo = time.time()
    hash_odnoy_chasti(zapisi)
    return time.time() - nachalo

def cpu_process(zapisi, kol_processov=config.PROCESS_COUNT):
    chasti = razbit_na_chasti(zapisi, kol_processov)
    nachalo = time.time()
    with ProcessPoolExecutor(max_workers=kol_processov) as executor:
        list(executor.map(hash_odnoy_chasti, chasti))
    return time.time() - nachalo

def benchmark(puti, zapisi=None):
    print(f"Запуск бенчмарка: {len(puti)} файлов, потоков: {config.THREAD_COUNT}, процессов: {config.PROCESS_COUNT}")
    t1, count1 = posledovatelnost(puti)
    print(f"Чтение файлов последовательно: {t1:.4f} сек. Записей: {count1}")
    t2, count2 = potoki(puti)
    print(f"Чтение файлов в потоках:       {t2:.4f} сек. Записей: {count2}")
    itog = {
        "files": len(puti),
        "io_times": {"posledovatelno": t1, "potoki": t2},
        "cpu_times": None,
        "data_size": 0
    }
    if zapisi:
        t3 = cpu_posledovatelno(zapisi)
        print(f"Хэши последовательно:          {t3:.4f} сек. (записей: {len(zapisi)})")
        t4 = cpu_process(zapisi)
        print(f"Хэши в процессах:              {t4:.4f} сек.")
        itog["cpu_times"] = {"posledovatelno": t3, "process": t4}
        itog["data_size"] = len(zapisi)
        if t4 < t3:
            print(f"Процессы быстрее в {t3 / t4:.2f} раз (CPU-задача)")
        else:
            print("На этом объеме процессы не дали выигрыша (возможно, мало данных)")

    if not os.path.exists(config.REPORTS_DIR):
        os.makedirs(config.REPORTS_DIR)
    put = os.path.join(config.REPORTS_DIR, "benchmark.json")
    try:
        with open(put, "w", encoding="utf-8") as f:
            json.dump(itog, f, ensure_ascii=False, indent=4)
        print(f"Результаты замера сохранены в файл: {put}")
    except Exception as e:
        print("Ошибка сохранения JSON:", e)
import numpy as np

def numpy_pokazateli(massiv):
    if len(massiv) == 0:
        return {"mean": 0, "min": 0, "max": 0, "median": 0, "std": 0}

    a = np.array(massiv, dtype=float)
    return {
        "mean": float(np.mean(a)),
        "min": float(np.min(a)),
        "max": float(np.max(a)),
        "median": float(np.median(a)),
        "std": float(np.std(a))
    }

def obschaya_statistika(zapisi):
    urovni = {}
    istochniki = {}
    oshibki_po_istochnikam = {}
    ip_adresa = {}
    oshibki_soobsheniya = {}
    po_chasam = {}

    for z in zapisi:
        if z.level not in urovni:
            urovni[z.level] = 0
        urovni[z.level] += 1

        if z.source not in istochniki:
            istochniki[z.source] = 0
        istochniki[z.source] += 1

        if z.level in ["ERROR", "CRITICAL"]:
            if z.source not in oshibki_po_istochnikam:
                oshibki_po_istochnikam[z.source] = 0
            oshibki_po_istochnikam[z.source] += 1

            if z.message not in oshibki_soobsheniya:
                oshibki_soobsheniya[z.message] = 0
            oshibki_soobsheniya[z.message] += 1

        if z.ip:
            if z.ip not in ip_adresa:
                ip_adresa[z.ip] = 0
            ip_adresa[z.ip] += 1

        chas_str = z.time.strftime("%Y-%m-%d %H")
        if chas_str not in po_chasam:
            po_chasam[chas_str] = 0
        po_chasam[chas_str] += 1
    spisok_znacheniy_chasov = list(po_chasam.values())

    return {
        "total": len(zapisi),
        "levels": urovni,
        "sources": istochniki,
        "errors_by_source": oshibki_po_istochnikam,
        "top_ips": ip_adresa,
        "top_error_messages": oshibki_soobsheniya,
        "events_by_hour": po_chasam,
        "numpy_stats": numpy_pokazateli(spisok_znacheniy_chasov)
    }

def sravnit_periodi(zapisi):
    if len(zapisi) < 2:
        return "Мало данных для сравнения"

    zapisi.sort(key=lambda z: z.time)

    seredina_idx = len(zapisi) // 2
    seredina_time = zapisi[seredina_idx].time
    pervie = {}
    vtorie = {}

    for z in zapisi:
        if z.time <= seredina_time:
            if z.source not in pervie: pervie[z.source] = 0
            pervie[z.source] += 1
        else:
            if z.source not in vtorie: vtorie[z.source] = 0
            vtorie[z.source] += 1

    print(f"\n--- СРАВНЕНИЕ ПЕРИОДОВ (середина: {seredina_time}) ---")
    vse_istochniki = set(list(pervie.keys()) + list(vtorie.keys()))

    for src in vse_istochniki:
        a = pervie.get(src, 0)
        b = vtorie.get(src, 0)
        raznica = b - a
        print(f"Источник {src}: до {a}, после {b} (разница: {raznica})")
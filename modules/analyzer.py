import pandas as pd
import numpy as np
import config
def sdelat_analiz(zapisi):
    data = []
    for zap in zapisi:
        data.append(zap.dict())
    if not data:
        print("Нет данных для анализа")
        return
    df = pd.DataFrame(data)
    df['time'] = pd.to_datetime(df['time'])

    print("--- ОБЩАЯ СТАТИСТИКА ---")
    print("Всего записей:", len(df))
    print("\n--- КОЛИЧЕСТВО ПО УРОВНЯМ ---")
    urovni = df['level'].value_counts()
    print(urovni)

    print("\n--- АКТИВНОСТЬ ИСТОЧНИКОВ ---")
    istochniki = df['source'].value_counts().head(config.TOP_COUNT)
    print(istochniki)

    print("\n--- ОШИБКИ ПО ИСТОЧНИКАМ ---")
    tolko_oshibki = df[df['level'].isin(['ERROR', 'CRITICAL'])]
    oshibki_po_istochikam = tolko_oshibki['source'].value_counts()
    print(oshibki_po_istochikam)

    print("\n--- АКТИВНЫЕ IP ---")
    ip_adressa = df['ip'].dropna().value_counts().head(config.TOP_COUNT)
    print(ip_adressa)

    print("\n--- ЧАСТЫЕ СООБЩЕНИЯ ОБ ОШИБКАХ ---")
    top_oshibok = tolko_oshibki['message'].value_counts().head(config.TOP_COUNT)
    print(top_oshibok)

    df['hour'] = df['time'].dt.hour
    sobytia_po_hour = df['hour'].value_counts().sort_index()
    massive_counts = np.array(sobytia_po_hour.values)
    print("\n--- СТАТИСТИКА АКТИВНОСТИ ПО ЧАСАМ (NumPy) ---")
    print("Количество событий по часам:")
    print(sobytia_po_hour)
    print()
    print("Среднее значение:", np.mean(massive_counts))
    print("Максимум:", np.max(massive_counts))
    print("Минимум:", np.min(massive_counts))
    print("Медиана:", np.median(massive_counts))
    print("Стандартное отклонение:", np.std(massive_counts))
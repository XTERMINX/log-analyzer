import pandas as pd
import config
from datetime import datetime

def poluchit_okno(vremya):
    okruglennaya_minuta = (vremya.minute // config.ANOMALY_WINDOW_MINUTES) * config.ANOMALY_WINDOW_MINUTES
    return f"{vremya.hour}:{okruglennaya_minuta}"

def seychas():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def nayti_anomalii(df):
    anomalii = []

    ip_okna = {}
    for _, row in df.iterrows():
        if pd.notna(row['ip']):
            vremya = datetime.strptime(row['time'], '%Y-%m-%d %H:%M:%S')
            klyuch = f"{row['ip']}_{poluchit_okno(vremya)}"
            ip_okna.setdefault(klyuch, []).append(str(row['message']))

    for klyuch, soobsheniya in ip_okna.items():
        count = len(soobsheniya)
        if count >= config.ANOMALY_IP_BURST:
            ip = klyuch.split("_")[0]
            anomalii.append({
                "type": "ip_burst",
                "time": seychas(),
                "source": ip,
                "severity": "CRITICAL",
                "reason": f"Резкий рост событий с IP {ip} ({count} за {config.ANOMALY_WINDOW_MINUTES} мин)",
                "records": soobsheniya[:3]
            })

    oshibki_okna = {}
    for _, row in df.iterrows():
        if row['level'] in ['ERROR', 'CRITICAL']:
            vremya = datetime.strptime(row['time'], '%Y-%m-%d %H:%M:%S')
            klyuch = f"{row['source']}_{poluchit_okno(vremya)}"
            oshibki_okna.setdefault(klyuch, []).append(str(row['message']))

    for klyuch, soobsheniya in oshibki_okna.items():
        count = len(soobsheniya)
        if count >= config.ANOMALY_ERROR_BURST:
            src = klyuch.split("_")[0]
            anomalii.append({
                "type": "error_burst",
                "time": seychas(),
                "source": src,
                "severity": "WARNING",
                "reason": f"Всплеск ошибок у {src} ({count} за {config.ANOMALY_WINDOW_MINUTES} мин)",
                "records": soobsheniya[:3]
            })

    povtory = {}
    for _, row in df.iterrows():
        klyuch = f"{row['source']}_{row['message']}"
        povtory.setdefault(klyuch, []).append(str(row['time']))

    for klyuch, vremena in povtory.items():
        count = len(vremena)
        if count >= config.ANOMALY_REPEAT_COUNT:
            src, msg = klyuch.split("_", 1)
            anomalii.append({
                "type": "repeating_message",
                "time": seychas(),
                "source": src,
                "severity": "INFO",
                "reason": f"Сообщение '{msg[:30]}...' повторилось {count} раз",
                "records": vremena[:3]
            })

    chasi_istochnikov = {}
    for _, row in df.iterrows():
        vremya = datetime.strptime(row['time'], '%Y-%m-%d %H:%M:%S')
        klyuch = f"{row['source']}_{vremya.date()}_{vremya.hour}"
        chasi_istochnikov.setdefault(klyuch, 0)
        chasi_istochnikov[klyuch] += 1

    po_istochnikam = {}
    for klyuch, count in chasi_istochnikov.items():
        src = klyuch.split("_")[0]
        po_istochnikam.setdefault(src, []).append(count)

    for src, counts in po_istochnikam.items():
        for i in range(1, len(counts)):
            srednee = sum(counts[:i]) / len(counts[:i])
            if srednee > 0 and counts[i] >= srednee * config.ANOMALY_ACTIVITY_JUMP:
                anomalii.append({
                    "type": "source_activity_jump",
                    "time": seychas(),
                    "source": src,
                    "severity": "WARNING",
                    "reason": f"Активность {src} выросла с {srednee:.1f} до {counts[i]} событий в час",
                    "records": []
                })
    return anomalii
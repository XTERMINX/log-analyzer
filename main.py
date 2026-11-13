import os
import config
import asyncio
import logging
import itertools
import pandas as pd
from datetime import datetime, timedelta
from utils.helpers import ensure_dirs, vvesti_datu, vvesti_chislo
from modules.importer import Importer, zagruzit_async
from modules.analyzer import sdelat_analiz
from modules.anomaly_detector import nayti_anomalii
from modules.filters import primenit_filtry,sortirovka, limit
from modules.statistics import obschaya_statistika, sravnit_periodi
from modules.storage import sohranit_zapisi, zagruzit_zapisi
from modules.exporter import save_json, save_csv
from modules.benchmark import benchmark

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logger.addHandler(console)
    try:
        fh = logging.FileHandler(config.LOG_FILE, encoding="utf-8")
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    except:
        pass

logger = logging.getLogger("main")

class LogApp:
    def __init__(self):
        self.importer = Importer()
        self.vse_zapisi = []

    def sgenerirovat_demo(self):
        ensure_dirs()
        with open(os.path.join(config.LOGS_DIR, "demo.txt"), "w", encoding="utf-8") as f:
            for i in range(50):
                vremya = datetime.now() - timedelta(minutes=i)
                f.write(f"{vremya.strftime('%Y-%m-%d %H:%M:%S')} | INFO | server_1 | Client connected\n")
        logger.info("Демо-данные созданы")

    def zagruzit_odin_fail(self):
        imya = input("Путь к файлу: ")
        for zap in self.importer.zagruzka_faila(imya):
            self.vse_zapisi.append(zap)
        print(f"Загружено: {self.importer.statistica['PASS']}, Ошибок: {self.importer.statistica['FAIL']}")

    def zagruzit_async_menu(self):
        puti = [os.path.join(config.LOGS_DIR, f) for f in os.listdir(config.LOGS_DIR) if f.endswith((".txt", ".csv"))]
        if not puti:
            print("Нет файлов для загрузки")
            return
        novye = asyncio.run(zagruzit_async(self.importer, puti))
        self.vse_zapisi = list(itertools.chain(self.vse_zapisi, novye))
        print(f"Всего записей: {len(self.vse_zapisi)}")

    def poisk(self):
        if not self.vse_zapisi:
            print("Нет данных!")
            return

        print("Введите условия (Enter для пропуска):")
        time_from = vvesti_datu("С даты: ")
        time_to = vvesti_datu("По дату: ")
        urovni_str = input("Уровни (через запятую): ").strip()
        urovni = [u.strip() for u in urovni_str.split(",")] if urovni_str else None
        ip = input("IP адрес: ").strip() or None
        source = input("Источник: ").strip() or None
        keyword = input("Ключевое слово: ").strip() or None
        res = primenit_filtry(
            self.vse_zapisi,
            time_from=time_from,
            time_to=time_to,
            urovni=urovni,
            ip=ip,
            source=source,
            keyword=keyword
        )
        sort_by = input("Сортировка (time/level, Enter - нет): ").strip() or None
        res = sortirovka(res, sort_by)
        kolvo = vvesti_chislo("Показать не более N записей (Enter - все): ")
        res = limit(res, kolvo)

        print(f"Найдено: {len(res)}")
        for z in res:
            print(z)

    def pokazat_analitiku(self):
        if not self.vse_zapisi:
            print("Нет данных")
            return
        sdelat_analiz(self.vse_zapisi)
        sravnit_periodi(self.vse_zapisi)

        df = pd.DataFrame([z.dict() for z in self.vse_zapisi])
        anomalii = nayti_anomalii(df)
        if anomalii:
            print("\n--- АНОМАЛИИ ---")
            for a in anomalii:
                print(f"[{a['severity']}] {a['source']}: {a['reason']}")
        else:
            print("\nАномалий не обнаружено")

    def sformirovat_otchet(self):
        if not self.vse_zapisi:
            print("Нет данных")
            return
        print("Сбор статистики")
        df = pd.DataFrame([z.dict() for z in self.vse_zapisi])
        anomalii = nayti_anomalii(df)
        stat = obschaya_statistika(self.vse_zapisi)

        otchet = {
            "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "files_processed": len(self.importer.zapomnil_faily),
            "total_records": len(self.vse_zapisi),
            "correct_records": self.importer.statistica["PASS"],
            "incorrect_records": self.importer.statistica["FAIL"],
            "levels": stat["levels"],
            "errors_by_source": stat["errors_by_source"],
            "top_ips": stat["top_ips"],
            "numpy_stats": stat["numpy_stats"],
            "anomalies_count": len(anomalii),
            "anomalies": anomalii
        }
        os.makedirs(config.REPORTS_DIR, exist_ok=True)
        save_json(otchet, "full_report.json")
        csv_dannye = {k: otchet[k] for k in
                      ["created", "files_processed", "total_records",
                       "correct_records", "incorrect_records", "anomalies_count"]}
        save_csv(csv_dannye, "full_report.csv")
        print("Отчет сохранен в папку data/reports!")

    def run(self):
        setup_logging()
        ensure_dirs()
        logger.info("Программа запущена")

        while True:
            print("\n=== LOG ANALYZER ===")
            print("1. Сгенерировать тестовые логи")
            print("2. Загрузить лог из файла")
            print("3. Асинхронная загрузка")
            print("4. Загрузить базу из JSON")
            print("5. Поиск и фильтрация")
            print("6. Показать аналитику и аномалии")
            print("7. Сохранить базу")
            print("8. Сформировать полный отчет (JSON/CSV)")
            print("9. Бенчмарк")
            print("0. Выход")
            vybor = input("Выбор: ")
            if vybor == "1":
                self.sgenerirovat_demo()
            elif vybor == "2":
                self.zagruzit_odin_fail()
            elif vybor == "3":
                self.zagruzit_async_menu()
            elif vybor == "4":
                self.vse_zapisi = zagruzit_zapisi()
                print(f"Загружено из базы: {len(self.vse_zapisi)}")
            elif vybor == "5":
                self.poisk()
            elif vybor == "6":
                self.pokazat_analitiku()
            elif vybor == "7":
                sohranit_zapisi(self.vse_zapisi)
            elif vybor == "8":
                self.sformirovat_otchet()
            elif vybor == "9":
                puti = [os.path.join(config.LOGS_DIR, f) for f in os.listdir(config.LOGS_DIR) if f.endswith(".txt")]
                if not puti:
                    print("Сначала создайте логи (пункт 1)")
                elif not self.vse_zapisi:
                    print("Сначала загрузите данные (пункт 2 или 3)")
                else:
                    benchmark(puti, self.vse_zapisi)
            elif vybor == "0":
                logger.info("Программа завершена")
                break
            else:
                print("Нет такого пункта")

if __name__ == "__main__":
    app = LogApp()
    app.run()
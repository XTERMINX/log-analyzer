import json
import csv
import os
import logging
import config

logger = logging.getLogger(__name__)

def save_json(data: dict, name: str = "report.json") -> None:
    put = os.path.join(config.REPORTS_DIR, name)
    os.makedirs(config.REPORTS_DIR, exist_ok=True)
    try:
        with open(put, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4, default=str)
        logger.info("Сохранено в JSON: %s", put)
    except Exception as e:
        logger.error("Ошибка сохранения JSON: %s", e)

def save_csv(stroki: list | dict, name: str = "report.csv") -> None:
    put = os.path.join(config.REPORTS_DIR, name)
    os.makedirs(config.REPORTS_DIR, exist_ok=True)
    if not stroki:
        logger.warning("Нет данных для CSV")
        return
    try:
        with open(put, "w", encoding="utf-8", newline="") as f:
            if isinstance(stroki, list) and isinstance(stroki[0], dict):
                writer = csv.DictWriter(f, fieldnames=stroki[0].keys())
                writer.writeheader()
                writer.writerows(stroki)
            elif isinstance(stroki, dict):
                writer = csv.writer(f)
                writer.writerow(["key", "value"])
                for k, v in stroki.items():
                    writer.writerow([k, v])
        logger.info("Сохранено в CSV: %s", put)
    except Exception as e:
        logger.error("Ошибка сохранения CSV: %s", e)
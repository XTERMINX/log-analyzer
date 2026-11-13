import json
import os
import logging
from datetime import datetime
import config
from modules.models import LogRecord

logger = logging.getLogger(__name__)

def zagruzit_zapisi() -> list[LogRecord]:
    if not os.path.exists(config.STORAGE_FILE):
        return []
    try:
        with open(config.STORAGE_FILE, "r", encoding="utf-8") as f:
            spisok = json.load(f)
    except Exception as e:
        logger.error("Ошибка чтения файла хранилища: %s", e)
        return []

    result = []
    for item in spisok:
        try:
            vremya = datetime.strptime(item["time"], "%Y-%m-%d %H:%M:%S")
            zap = LogRecord(
                time=vremya, level=item["level"], source=item["source"],
                message=item["message"], ip=item.get("ip"), code=item.get("code")
            )
            result.append(zap)
        except Exception as e:
            logger.warning("Битая запись в хранилище: %s", e)
    return result

def sohranit_zapisi(zapisi: list[LogRecord]) -> None:
    starie = zagruzit_zapisi()
    starye_klyuchi = set(z.klyuch() for z in starie)
    vse_zapisi = list(starie)
    novyh = 0
    for z in zapisi:
        k = z.klyuch()
        if k not in starye_klyuchi:
            vse_zapisi.append(z)
            starye_klyuchi.add(k)
            novyh += 1
    dannye = [z.dict() for z in vse_zapisi]
    try:
        os.makedirs(os.path.dirname(config.STORAGE_FILE), exist_ok=True)
        with open(config.STORAGE_FILE, "w", encoding="utf-8") as f:
            json.dump(dannye, f, ensure_ascii=False, indent=4)
        logger.info("Сохранено %d новых записей. Всего в базе: %d", novyh, len(vse_zapisi))
    except Exception as e:
        logger.error("Ошибка сохранения базы: %s", e)
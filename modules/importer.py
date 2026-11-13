import json
import config
import csv
import os
import asyncio
import logging
from datetime import datetime
from functools import lru_cache
from typing import Generator, List
from modules.models import LogRecord
from modules.parser import opredelit_format

logger = logging.getLogger(__name__)

@lru_cache(maxsize=1000)
def sozdat_datu(stroka: str) -> datetime | None:
    try:
        return datetime.strptime(stroka, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return None

def proverka_urovna(lvl: str) -> bool:
    return lvl in config.VALID_LEVELS

class Importer:
    def __init__(self):
        self.zapomnil_faily = []
        self.statistica = {"PASS": 0, "FAIL": 0}

    def chtenie_txt(self, put: str) -> Generator[LogRecord, None, None]:
        try:
            with open(put, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line: continue
                    parts = line.split(' | ')
                    if len(parts) < 4:
                        self.statistica["FAIL"] += 1
                        continue
                    d = sozdat_datu(parts[0])
                    if d is None or not proverka_urovna(parts[1]):
                        self.statistica["FAIL"] += 1
                        continue
                    self.statistica["PASS"] += 1
                    yield LogRecord(time=d, level=parts[1], source=parts[2], message=parts[3])
        except FileNotFoundError:
            logger.error("Файл не найден: %s", put)

    def chtenie_csv(self, put: str) -> Generator[LogRecord, None, None]:
        try:
            with open(put, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        if row.get('time') is None or row.get('level') is None or row.get('message') is None:
                            self.statistica["FAIL"] += 1
                            continue
                        d = sozdat_datu(row['time'])
                        if d is None or not proverka_urovna(row['level']):
                            self.statistica["FAIL"] += 1
                            continue
                        self.statistica["PASS"] += 1
                        yield LogRecord(
                            time=d, level=row['level'], source=row['source'],
                            message=row['message'], ip=row.get('ip'), code=row.get('code')
                        )
                    except Exception:
                        self.statistica["FAIL"] += 1
        except FileNotFoundError:
            logger.error("Файл не найден: %s", put)

    def chtenie_json(self, put: str) -> Generator[LogRecord, None, None]:
        try:
            with open(put, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line: continue
                    try:
                        data = json.loads(line)
                        d = sozdat_datu(data['time'])
                        if d is None or not proverka_urovna(data['level']):
                            self.statistica["FAIL"] += 1
                            continue
                        self.statistica["PASS"] += 1
                        yield LogRecord(
                            time=d, level=data['level'], source=data['source'],
                            message=data['message'], ip=data.get('ip'), code=data.get('code')
                        )
                    except json.JSONDecodeError:
                        self.statistica["FAIL"] += 1
        except FileNotFoundError:
            logger.error("Файл не найден: %s", put)

    def zagruzka_faila(self, put: str) -> Generator[LogRecord, None, None]:
        if put in self.zapomnil_faily:
            print(f"Файл {put} уже был загружен ранее. Пропускаем.")
            return
        if not os.path.exists(put):
            print(f"Ошибка: Файл не найден — {put}")
            return
        fmt = opredelit_format(put)
        if fmt is None:
            logger.error("Неизвестный формат файла: %s", put)
            return
        self.zapomnil_faily.append(put)
        if fmt == "txt":
            yield from self.chtenie_txt(put)
        elif fmt == "csv":
            yield from self.chtenie_csv(put)
        elif fmt == "json":
            yield from self.chtenie_json(put)

async def zagruzit_odin_fail_async(imp: Importer, put: str) -> List[LogRecord]:
    return await asyncio.to_thread(lambda: list(imp.zagruzka_faila(put)))

async def zagruzit_async(imp: Importer, puti: List[str]) -> List[LogRecord]:
    logger.info("Запуск асинхронной загрузки")
    zadachi = [zagruzit_odin_fail_async(imp, put) for put in puti]
    results = await asyncio.gather(*zadachi)
    vse_zapisi = []
    for spisok in results:
        vse_zapisi.extend(spisok)
    logger.info("Асинхронно загружено: %d записей", len(vse_zapisi))
    return vse_zapisi
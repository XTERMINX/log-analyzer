from datetime import datetime
import hashlib
class LogRecord:
    def __init__(self, time: datetime, level: str, source: str, message: str, ip: str = None, code: str = None,extra: dict = None):
        self.time = time
        self.level = level
        self.source = source
        self.message = message
        self.ip = ip
        self.code = code
        self.extra = extra if extra is not None else {}

    def __str__(self) -> str:
        s = f"[{self.time}] | {self.level} | {self.source} | {self.message}"
        if self.ip:
            s += f" | IP: {self.ip}"
        if self.code:
            s += f" | Code: {self.code}"
        return s

    def klyuch(self) -> str:
        s = f"{self.time}|{self.level}|{self.source}|{self.message}|{self.ip}|{self.code}"
        return hashlib.sha1(s.encode("utf-8")).hexdigest()

    def dict(self) -> dict:
        timestr = self.time.strftime('%Y-%m-%d %H:%M:%S')
        result = {
            'time': timestr,
            'level': self.level,
            'source': self.source,
            'message': self.message,
            'ip': self.ip,
            'code': self.code,
            'extra': self.extra
        }
        return result

class LogIterator:
    def __init__(self, zapisi):
        self.zapisi = zapisi
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.index >= len(self.zapisi):
            raise StopIteration
        tekushaya = self.zapisi[self.index]
        self.index += 1
        return tekushaya
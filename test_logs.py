import pytest
import pandas as pd
from datetime import datetime
import json
import config
from modules.models import LogRecord
from utils import validators
from modules import filters
from modules.statistics import numpy_pokazateli, obschaya_statistika
from modules.anomaly_detector import nayti_anomalii
from modules import exporter

@pytest.fixture
def sample_logs():
    z1 = LogRecord(datetime(2026, 9, 12, 10, 0, 0), "ERROR", "server_1", "Database timeout", ip="192.168.1.1")
    z2 = LogRecord(datetime(2026, 9, 12, 11, 0, 0), "INFO", "server_2", "User logged in", ip="192.168.1.2")
    z3 = LogRecord(datetime(2026, 9, 12, 12, 0, 0), "WARNING", "server_1", "High memory", ip="192.168.1.1")
    return [z1, z2, z3]

def _df_from(zapisi):
    return pd.DataFrame([z.dict() for z in zapisi])

def test_log_record_creation():
    zap = LogRecord(datetime(2026, 9, 12, 10, 0, 0), "INFO", "server", "msg")
    assert zap.level == "INFO"
    assert zap.ip is None

    slovar = zap.dict()
    assert slovar["time"] == "2026-09-12 10:00:00"
    assert slovar["source"] == "server"

def test_log_record_hash():
    z1 = LogRecord(datetime(2026, 9, 12, 10, 0, 0), "ERROR", "srv", "msg")
    z2 = LogRecord(datetime(2026, 9, 12, 10, 0, 0), "ERROR", "srv", "msg")
    z3 = LogRecord(datetime(2026, 9, 12, 10, 0, 1), "ERROR", "srv", "msg")

    assert z1.klyuch() == z2.klyuch()
    assert z1.klyuch() != z3.klyuch()

@pytest.mark.parametrize("ip, expected", [
    ("192.168.1.1", True),
    ("10.0.0.255", True),
    ("999.1.1.1", False),
    ("192.168.1", False),
    ("abc.def.ghi.jkl", False),
    ("", False),
    (None, False)
])
def test_proverit_ip(ip, expected):
    assert validators.proverit_ip(ip) == expected

@pytest.mark.parametrize("date_str, expected", [
    ("2026-09-12 10:00:00", True),
    ("2026-09-12T10:00:00", False),
    ("12.09.2026 10:00:00", False),
    ("", False),
    (None, False)
])
def test_razobrat_vremya(date_str, expected):
    result = validators.razobrat_vremya(date_str)
    if expected:
        assert isinstance(result, datetime)
    else:
        assert result is None

def test_filter_by_level(sample_logs):
    result = filters.primenit_filtry(sample_logs, urovni=["ERROR"])
    assert len(result) == 1
    assert result[0].message == "Database timeout"

def test_filter_by_ip(sample_logs):
    result = filters.primenit_filtry(sample_logs, ip="192.168.1.1")
    assert len(result) == 2

def test_filter_combined(sample_logs):
    result = filters.primenit_filtry(sample_logs, urovni=["ERROR", "WARNING"], keyword="timeout")
    assert len(result) == 1
    assert result[0].level == "ERROR"

def test_filter_no_results(sample_logs):
    result = filters.primenit_filtry(sample_logs, keyword="такого-слова-нет")
    assert len(result) == 0

def test_save_and_load_preset(tmp_path, monkeypatch):
    test_file = tmp_path / "test_presets.json"
    monkeypatch.setattr("modules.filters.config.PRESETS_FILE", str(test_file))
    params = {"urovni": ["ERROR"], "keyword": "test"}
    filters.save_preset("my_test_preset", params)
    loaded = filters.load_preset("my_test_preset")
    assert loaded is not None
    assert loaded["urovni"] == ["ERROR"]
    assert loaded["keyword"] == "test"

def test_numpy_pokazateli():
    res = numpy_pokazateli([1, 2, 3, 4])
    assert res["mean"] == 2.5
    assert res["min"] == 1.0
    assert res["max"] == 4.0
    assert res["median"] == 2.5

def test_numpy_pokazateli_pustoy():
    res = numpy_pokazateli([])
    assert res["mean"] == 0

def test_obschaya_statistika(sample_logs):
    res = obschaya_statistika(sample_logs)
    assert res["total"] == 3
    assert res["levels"]["ERROR"] == 1
    assert res["errors_by_source"]["server_1"] == 1

def test_anomaly_ip_burst():
    zapisi = [LogRecord(datetime(2026, 9, 12, 10, i % 10, 0), "INFO", "srv", f"msg {i}", ip="1.1.1.1")
              for i in range(config.ANOMALY_IP_BURST + 5)]
    anomalii = nayti_anomalii(_df_from(zapisi))
    assert "ip_burst" in [a["type"] for a in anomalii]
    a = [x for x in anomalii if x["type"] == "ip_burst"][0]
    assert a["source"] == "1.1.1.1"
    assert a["severity"] in ["INFO", "WARNING", "CRITICAL"]
    assert a["reason"]
    assert a["time"]

def test_anomaly_repeating_message():
    zapisi = [LogRecord(datetime(2026, 9, 12, 10, i, 0), "INFO", "srv", "same message")
              for i in range(config.ANOMALY_REPEAT_COUNT + 2)]
    anomalii = nayti_anomalii(_df_from(zapisi))
    assert "repeating_message" in [a["type"] for a in anomalii]

def test_anomaly_no_false_positives():
    zapisi = [LogRecord(datetime(2026, 9, 12, 10, i, 0), "INFO", "srv", f"msg {i}", ip=f"1.1.1.{i}")
              for i in range(1, 9)]
    anomalii = nayti_anomalii(_df_from(zapisi))
    assert anomalii == []

def test_exporter_json(tmp_path, monkeypatch):
    monkeypatch.setattr("modules.exporter.config.REPORTS_DIR", str(tmp_path))
    exporter.save_json({"a": 1, "b": "тест"}, "t.json")
    put = tmp_path / "t.json"
    assert put.exists()
    with open(put, encoding="utf-8") as f:
        dannye = json.load(f)
    assert dannye["a"] == 1

def test_exporter_csv(tmp_path, monkeypatch):
    monkeypatch.setattr("modules.exporter.config.REPORTS_DIR", str(tmp_path))
    exporter.save_csv([{"x": 1, "y": 2}], "t.csv")
    put = tmp_path / "t.csv"
    assert put.exists()
    soderzhimoe = put.read_text(encoding="utf-8")
    assert "x" in soderzhimoe and "1" in soderzhimoe
import os
VALID_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOGS_DIR = os.path.join(DATA_DIR, "logs")
REPORTS_DIR = os.path.join(DATA_DIR, "reports")
STORAGE_FILE = os.path.join(DATA_DIR, "storage.json")
PRESETS_FILE = os.path.join(DATA_DIR, "filters_presets.json")
LOG_FILE = os.path.join(DATA_DIR, "app.log")
LOG_LEVEL = "INFO"
THREAD_COUNT = 4
PROCESS_COUNT = 4
ANOMALY_IP_BURST = 40
ANOMALY_ERROR_BURST = 15
ANOMALY_REPEAT_COUNT = 10
ANOMALY_WINDOW_MINUTES = 10
ANOMALY_ACTIVITY_JUMP = 3.0
TOP_COUNT = 5

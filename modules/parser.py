import os

def opredelit_format(put: str):
    ext = os.path.splitext(put)[1].lower()
    if ext == ".txt" or ext == ".log":
        return "txt"
    elif ext == ".csv":
        return "csv"
    elif ext == ".json":
        return "json"
    else:
        return None
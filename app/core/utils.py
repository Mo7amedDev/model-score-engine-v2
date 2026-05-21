import json 
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" 

def saveJsonData(data, filename):
    path = DATA_DIR / filename
    path.parent.mkdir(parents=True, exist_ok=True)  # ensure folder exists
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

def loadJsonData(filename):
    path = DATA_DIR / filename
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)
    
    
# ====================== ERROR SAVED =====================

import traceback
from datetime import datetime

def saveErrorLog(error: Exception, filename="errors.json"):
    path = DATA_DIR / filename
    path.parent.mkdir(parents=True, exist_ok=True)

    error_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "error_type": type(error).__name__,
        "message": str(error),
        "traceback": traceback.format_exc()
    }

    # load existing logs
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            try:
                logs = json.load(f)
            except:
                logs = []
    else:
        logs = []

    logs.append(error_entry)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=4, ensure_ascii=False)
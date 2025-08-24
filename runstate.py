import json
import pathlib
from datetime import date

RUNSTATE_FILE = pathlib.Path(__file__).parent / ".runstate.json"

def make_sure_exists():
    if not RUNSTATE_FILE.exists():
        RUNSTATE_FILE.write_text("{}")  # create empty JSON object

def load_data():
    with open(RUNSTATE_FILE, "r") as f:
        data = json.load(f)

    today_str = date.today().isoformat()

    if data.get("date") == today_str:
        return True
    else:
        return False

def save_data():
    today_str = date.today().isoformat()
    with open(RUNSTATE_FILE, "w") as f:
        json.dump({"date": today_str}, f)

from datetime import datetime
import os
from zoneinfo import ZoneInfo


job_id = datetime.now(ZoneInfo("Europe/Warsaw")).strftime("%Y-%m-%d-%H-%M-%S")
BASE_PATH = "./db/fifa/"
SOURCE_PATH = os.path.join(BASE_PATH, "source_data")
OUTPUT_PATH = os.path.join(BASE_PATH, "jobs", job_id)
PAGE_ID_LABEL = "PAGE_ID"
SESSION_STATS_JSON_FILENAME = "session_stats.json"

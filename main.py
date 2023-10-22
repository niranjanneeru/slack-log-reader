from src import utils, slack
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

with open('timestamp.txt') as f :
    timestamp_from = int(f.read().strip())

timestamp_to = int(datetime.now().timestamp())

# CONVERTING TIMESTAMP TO DATE
try:
    from_time = utils.to_date(timestamp_from)
    to_time = utils.to_date(timestamp_to)
except Exception as e:
    exit(1)

incidents  = slack.work(timestamp_from, timestamp_to, from_time, to_time)

if len(incidents) > 0:
    with open('timestamp.txt', 'w') as f :
        incident = list(incidents.values())[0]
        f.write(str(incident[2]))
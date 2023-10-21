from src import utils, slack
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()
timestamp_from = int((datetime.now() - timedelta(days=1)).timestamp())
timestamp_to = int(datetime.now().timestamp())

# CONVERTING TIMESTAMP TO DATE
try:
    from_time = utils.to_date(timestamp_from)
    to_time = utils.to_date(timestamp_to)
except Exception as e:
    exit(1)

slack.work(timestamp_from, timestamp_to, from_time, to_time)
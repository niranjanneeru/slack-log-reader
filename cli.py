import argparse
from src import utils, slack
from dotenv import load_dotenv

load_dotenv()

# ARGUMENT PARSING
parser = argparse.ArgumentParser(
    description="A simple python script to summarise prod alert logs in slack with command-line arguments."
)
parser.add_argument("--begin", help="Format is DD-MM-YYYY HH:MM:SS (24 hr format)")
parser.add_argument("--end", help="Format is DD-MM-YYYY HH:MM:SS (24 hr format)")
parser.add_argument("--mode", help="Modes - gcp kubernetes")
args = parser.parse_args()

from_time = args.begin
to_time = args.end
mode = args.mode

# CONVERTING INPUT TIME TO TIMESTAMP
try:
    timestamp_from = utils.to_timestamp(from_time)
    timestamp_to = utils.to_timestamp(to_time)
except Exception as e:
    print("Invalid arguments, please use python3 main.py --help")
    exit(1)

slack.work(timestamp_from, timestamp_to, from_time, to_time)
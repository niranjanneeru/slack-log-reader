import os
import argparse
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from src import utils
from dotenv import load_dotenv

load_dotenv()


parser = argparse.ArgumentParser(
    description="A simple python script to summarise prod alert logs in slack with command-line arguments."
)
parser.add_argument("--begin", help="Format is DD-MM-YYYY HH:MM:SS (24 hr format)")
parser.add_argument("--end", help="Format is DD-MM-YYYY HH:MM:SS (24 hr format)")
args = parser.parse_args()
from_time = args.begin
to_time = args.end

try:
    timestamp_from = utils.to_timestamp(from_time)
    timestamp_to = utils.to_timestamp(to_time)
except Exception as e:
    print("Invalid arguments, please use python3 main.py --help")
    exit(1)

result = ""

try:
    channel_id = os.environ["LOG_CHANNEL_ID"]
    client = WebClient(token=os.environ["SLACK_API_KEY"])
    
    messages = utils.get_all_messages(client, timestamp_from, timestamp_to, channel_id)
    
    print("\n--TOTAL MESSAGES DURING THIS TIMEFRAME: ", len(messages), "\n")
    result += f"TIMEFRAME: {from_time} to {to_time}\nTOTAL ALERTS: {len(messages)}\n\n"
    
    incidents = {}

    for message in messages[::-1]:
        if "text" in message:
            action, link, link_id, process = utils.parse_text(message["text"])
            if action == "Incident":
                if process == "running":
                    incidents[link_id] = link
                if process == "stopped":
                    try:
                        del incidents[link_id]
                    except:
                        pass

    result += "Type: GCP\n\n"
    for k, v in incidents.items():
        result += f"ID: {k} Link: {v}\n"
        print("ID: ", k, " Link: ", v)
    result += f"\nCRITICAL ALERTS PENDING: {len(incidents)}\n"
    print("\n--NUMBER OF CRITICAL ALERTS PENDING: ", len(incidents), "\n")

    if len(incidents) > 0 : client.chat_postMessage(channel=os.environ['REPORTING_CHANNEL_ID'], text = result, unfurl_links=False)

except SlackApiError as e:
    print(f"Error: {e.response['error']}")

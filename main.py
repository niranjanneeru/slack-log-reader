import os
import argparse
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


def to_timestamp(date_string):
    date_format = "%d-%m-%Y %H:%M:%S"
    date_obj = datetime.strptime(date_string, date_format)
    return int(date_obj.timestamp())


def parse_text(text):
    if not text.startswith("Incident"):
        return None, None, None, None
    lines = text.split("\n")
    rest = lines[0].split(" ")
    action = rest[0]
    link, link_id = rest[1][1:-1].split("|")
    process = "stopped" if rest[2] == "stopped" else "running"
    return action, link, link_id, process


def get_all_messages():
    result = client.conversations_history(
        channel=channel_id,
        oldest=timestamp_from,
        latest=timestamp_to,
        limit=200,
        inclusive=True,
    )

    messages = result["messages"]
    latest_message = messages[-1]

    while result["has_more"]:
        result = client.conversations_history(
            channel=channel_id,
            oldest=timestamp_from,
            latest=latest_message["ts"],
            limit=200,
            inclusive=True,
        )

        latest_message = result["messages"][-1]

        for m in result["messages"]:
            messages.append(m)

    return messages


parser = argparse.ArgumentParser(
    description="A simple python script to summarise prod alert logs in slack with command-line arguments."
)
parser.add_argument("--begin", help="Format is DD-MM-YYYY HH:MM:SS (24 hr format)")
parser.add_argument("--end", help="Format is DD-MM-YYYY HH:MM:SS (24 hr format)")
args = parser.parse_args()
from_time = args.begin
to_time = args.end

client = WebClient(token=os.environ["SLACK_API_KEY"])

channel_id = os.environ["LOG_CHANNEL_ID"]

try:
    timestamp_from = to_timestamp(from_time)
    timestamp_to = to_timestamp(to_time)
except Exception as e:
    print("Invalid arguments, please use python3 main.py --help")
    exit(1)

try:
    messages = get_all_messages()
    print("\n--TOTAL MESSAGES DURING THIS TIMEFRAME: ", len(messages), "\n")
    incidents = {}

    for message in messages[::-1]:
        if "text" in message:
            action, link, link_id, process = parse_text(message["text"])
            if action == "Incident":
                if process == "running":
                    incidents[link_id] = link
                if process == "stopped":
                    try:
                        del incidents[link_id]
                    except:
                        pass

    for k, v in incidents.items():
        print("ID: ", k, " Link: ", v)
    print("\n--NUMBER OF CRITICAL ALERTS PENDING: ", len(incidents), "\n")

except SlackApiError as e:
    print(f"Error: {e.response['error']}")

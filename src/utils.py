import os
import argparse
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from datetime import datetime

def to_timestamp(date_string):
    date_format = "%d-%m-%Y %H:%M:%S"
    date_obj = datetime.strptime(date_string, date_format)
    return int(date_obj.timestamp())

def to_date(timestamp):
    date_obj = datetime.fromtimestamp(timestamp)
    date_string = date_obj.strftime("%d-%m-%Y %H:%M:%S")
    return date_string


def parse_text(text):
    if not text.startswith("Incident"):
        return None, None, None, None
    lines = text.split("\n")
    rest = lines[0].split(" ")
    action = rest[0]
    link, link_id = rest[1][1:-1].split("|")
    process = "stopped" if rest[2] == "stopped" else "running"
    return action, link, link_id, process


def get_all_messages(client, timestamp_from, timestamp_to, channel_id):
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

import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from . import utils

def work(timestamp_from, timestamp_to, from_time, to_time):

    result = ""
    blocks = []

    # READING & PROCESSING SLACK ALERTS
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
                details = message["attachments"][0] if "attachments" in message else None
                details = details["text"] if "text" in message else None
                timestamp = int(float(message['ts']))
                if action == "Incident":
                    if process == "running":
                        incidents[link_id] = link, details, timestamp
                    if process == "stopped":
                        try:
                            del incidents[link_id]
                        except:
                            pass

        result += "Type: GCP\n\n"
        for k, v in incidents.items():
            result += f"[{utils.to_date(v[2])}] ID: <{v[0]}|{k}> \n ALERT: {v[1]} \n\n"
            print("ID: ", k, " Link: ", v[0], " Details: ", v[1])
        result += f"\nCRITICAL ALERTS PENDING: {len(incidents)}\n"
        print("\n--NUMBER OF CRITICAL ALERTS PENDING: ", len(incidents), "\n")

        if len(incidents) > 0:
            client.chat_postMessage(
                channel=os.environ["REPORTING_CHANNEL_ID"],
                text=result,
                mrkdwn=True,
                unfurl_links=False,
            )

    except SlackApiError as e:
        print(f"Error: {e.response['error']}")

    return incidents

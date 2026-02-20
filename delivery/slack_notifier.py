import os
import requests


def send_to_slack(title, content):
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")

    if not webhook_url:
        print("Slack webhook not set")
        return

    payload = {
        "text": f"*{title}*\n```{content}```"
    }

    response = requests.post(webhook_url, json=payload)

    if response.status_code != 200:
        print("Slack error:", response.text)

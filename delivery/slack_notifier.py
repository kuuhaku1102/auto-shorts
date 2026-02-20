import os
import requests


def send_to_slack(title: str, content: str):
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook_url:
        print("SLACK_WEBHOOK_URL is not set. Skip slack notification.")
        return

    # Slackの投稿は長すぎると切れるので、念のため少し短縮（必要なら調整）
    max_len = 3500
    if len(content) > max_len:
        content = content[:max_len] + "\n...(truncated)"

    payload = {
        "text": f"*{title}*\n```{content}```"
    }

    resp = requests.post(webhook_url, json=payload, timeout=30)
    if resp.status_code != 200:
        raise RuntimeError(f"Slack webhook failed: {resp.status_code} {resp.text}")

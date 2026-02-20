import os
import requests


def _post_to_webhook(webhook_url: str, payload: dict):
    resp = requests.post(webhook_url, json=payload, timeout=30)
    if resp.status_code != 200:
        raise RuntimeError(f"Slack webhook failed: {resp.status_code} {resp.text}")


def send_to_slack(title: str, content: str, cards: list[dict] | None = None):
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
    _post_to_webhook(webhook_url, payload)

    if not cards:
        return

    for card in cards:
        rank = card.get("rank", "-")
        name = card.get("name", "不明カード")
        image_url = card.get("image_url")
        detail_url = card.get("detail_url")

        body = f"#{rank} {name}"
        if detail_url:
            body += f"\n{detail_url}"

        if image_url:
            card_payload = {
                "text": body,
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": body
                        }
                    },
                    {
                        "type": "image",
                        "image_url": image_url,
                        "alt_text": f"{name} image"
                    }
                ]
            }
        else:
            card_payload = {"text": body}

        _post_to_webhook(webhook_url, card_payload)

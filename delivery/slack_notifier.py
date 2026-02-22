import os
import time
from urllib.parse import urlparse
import requests


def _post_to_webhook(webhook_url: str, payload: dict):
    max_attempts = 3

    for attempt in range(1, max_attempts + 1):
        resp = requests.post(webhook_url, json=payload, timeout=30)
        if resp.status_code == 200:
            return

        if resp.status_code == 429 and attempt < max_attempts:
            retry_after = int(resp.headers.get("Retry-After", "1"))
            time.sleep(max(retry_after, 1))
            continue

        raise RuntimeError(f"Slack webhook failed: {resp.status_code} {resp.text}")


def _format_price(price) -> str:
    if isinstance(price, int):
        return f"¥{price:,}"
    if isinstance(price, float):
        return f"¥{int(price):,}"
    if price is None:
        return "-"
    return str(price)


def _image_file_name(card: dict) -> str:
    image_url = card.get("image_url")
    if not image_url:
        return f"card{card.get('rank', 'x')}.jpg"

    parsed = urlparse(image_url)
    file_name = os.path.basename(parsed.path)
    return file_name or f"card{card.get('rank', 'x')}.jpg"


def _build_ranking_data_block(cards: list[dict]) -> str:
    lines = ["const rankingData = ["]
    for card in cards:
        rank = card.get("rank", "-")
        name = str(card.get("name", "不明カード")).replace('"', '\\"')
        price = _format_price(card.get("price")).replace('"', '\\"')
        image = _image_file_name(card).replace('"', '\\"')
        lines.append(
            f'  {{ rank: {rank}, name: "{name}", price: "{price}", image: "{image}" }},'
        )
    lines.append("];")
    return "\n".join(lines)


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
    try:
        _post_to_webhook(webhook_url, payload)
    except Exception as exc:
        print(f"Failed to send script message to Slack: {exc}")
        return

    if not cards:
        return

    ranking_data = _build_ranking_data_block(cards)
    ranking_payload = {
        "text": "📦 rankingData\n```" + ranking_data + "```"
    }
    try:
        _post_to_webhook(webhook_url, ranking_payload)
    except Exception as exc:
        print(f"Failed to send rankingData to Slack: {exc}")

    for card in cards:
        rank = card.get("rank", "-")
        name = card.get("name", "不明カード")
        price = _format_price(card.get("price"))
        image_url = card.get("image_url")
        detail_url = card.get("detail_url")

        body = f"#{rank} {name}\n価格: {price}"
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

        try:
            _post_to_webhook(webhook_url, card_payload)
        except Exception as exc:
            print(f"Failed to send card notification (rank={rank}, name={name}): {exc}")

from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def build_fixed_part(label, items):
    lines = []

    lines.append(f"{label}")
    lines.append("")

    for item in items:
        line = (
            f"第{item['rank']}位は {item['name']}。"
            f"直近価格は {item['price']:,}円。"
            f"7日間で {item['change_rate']:+.2f}%。"
        )

        if item.get("diff_from_yesterday") is not None:
            diff = item["diff_from_yesterday"]
            sign = "+" if diff >= 0 else ""
            line += f"前日比は {sign}{diff:,}円。"

        if item.get("consecutive_days"):
            line += f"{item['consecutive_days']}回ランクイン中。"

        lines.append(line)

    return "\n".join(lines)


def build_ai_comment(label, items):
    summary = "\n".join(
        [
            f"{item['name']} 価格:{item['price']} 7日:{item['change_rate']}%"
            for item in items
        ]
    )

    prompt = f"""
以下はポケモンカードのランキングデータです。

{summary}

このデータを踏まえて、
YouTube Shorts向けに
投資目線で自然な20秒以内の分析コメントを1段落で作成してください。
煽りすぎず、プロっぽく。
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()


def build_script(label, items):
    fixed = build_fixed_part(label, items)
    ai_comment = build_ai_comment(label, items)

    return f"{fixed}\n\n{ai_comment}"

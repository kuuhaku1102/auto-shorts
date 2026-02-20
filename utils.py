def clean_price(price_str):
    return int(price_str.replace("円", "").replace(",", "").strip())

def clean_rate(rate_str):
    return float(
        rate_str.replace("%", "")
                .replace("+", "")
                .replace("−", "-")
                .strip()
    )

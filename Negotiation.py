def calculate_offer(price):
    if price <= 3000:
        return price - 400

    elif price <= 5000:
        return price - 700

    return price - 1000


def generate_message(title, offer):
    return f"""
Hey mate, would you take ${offer} cash today for {title}?

Can pick up ASAP.
"""

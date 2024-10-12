import time
import random
import string
import re
import asyncio
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


async def check_card(card_info, proxy, profile):
    """Simulates checking a card by making a fake request and returning a response."""
    card = card_info.split("|")
    if len(card) != 4 or not all(card):
        return f"Invalid card details for `{card_info}`."

    cc, mm, yy, cvv = card
    results = []

    # Simulate checking the card (replace this part with actual logic)
    async with ClientSession() as session:
        # Simulate Stripe or other request logic here
        await asyncio.sleep(random.uniform(0.5, 1.5))  # Simulate delay for request

        # Randomly generate a fake status for demonstration purposes
        status = random.choice(["Approved ✅", "Declined ❌", "Insufficient Funds 💰", "Live ✅"])
        response_message = random.choice(["Payment Successful", "Invalid Account", "Card Requires Verification"])

        results.append(
            f"𝗖𝗮𝗿𝗱: `{cc}|{mm}|{yy}|{cvv}`\n𝗦𝘁𝗮𝘁𝘂𝘀: {status}\n𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲: {response_message}\n"
        )

    return "\n".join(results)


async def process_cards_concurrently(cards_info):
    """Processes multiple cards concurrently."""
    tasks = []
    for card_info in cards_info:
        proxy = next(proxy_gen)  # Get the next proxy
        profile = generate_random_profile()  # Generate random profile for the card
        tasks.append(check_card(card_info, proxy, profile))

    # Run all the tasks concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results


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
    if len(cards_info) > 1000:
        print("The maximum number of cards allowed is 30. Please reduce the number of cards and try again.")
        return

    # Process the cards
    print("Processing your cards...")
    start_time = time.time()

    try:
        results = await process_cards_concurrently(cards_info[:10])  # Limit to 10 for demonstration

        final_response = "𝗠𝗮𝘀𝘀 𝗖𝗵𝗲𝗰𝗸𝗲𝗿\n\n"
        final_response += "\n\n".join(results)
        final_response += f"\n\n𝗧𝗶𝗺𝗲: {round(time.time() - start_time, 2)}s"

        # Print final results
        print(final_response)

    except Exception as e:
        print(f"An error occurred: {str(e)}")


# Run the main function in the event loop
if __name__ == "__main__":
    asyncio.run(main())
      

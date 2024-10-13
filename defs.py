import asyncio
import random


async def charge_resp(result):
    try:
        if (
            '"payment_success": true' in result
            or '"payment_success": false' not in result
        ):
            response = "Charged 1$ 🔥"
        elif "insufficient funds" in result or "card has insufficient funds." in result:
            response = "Insufficient Funds ❎"
        elif (
            "incorrect_cvc" in result
            or "security code is incorrect." in result
            or "Your card's security code is incorrect." in result
        ):
            response = "CCN Live ❎"
        elif "transaction_not_allowed" in result:
            response = "Card Doesn't Support Purchase"
        elif '"cvc_check": "pass"' in result:
            response = "CVV LIVE ❎"
        elif (
            "three_d_secure_redirect" in result
            or "card_error_authentication_required" in result
        ):
            response = "3D Challenge Required ❎"
        elif "stripe_3ds2_fingerprint" in result:
            response = "3D Challenge Required ❎"
        elif "Your card does not support this type of purchase." in result:
            response = "Card Doesn't Support Purchase ❎"
        elif (
            "generic_decline" in result
            or "You have exceeded the maximum number of declines on this card in the last 24 hour period."
            in result
            or "card_decline_rate_limit_exceeded" in result
        ):
            response = "Generic Decline 🚫"
        elif "do not honor" in result:
            response = "Do Not Honor 🚫"
        elif "fraudulent" in result:
            response = "Fraudulent 🚫 "
        elif "setup_intent_authentication_failure" in result:
            response = "setup_intent_authentication_failure 🚫"
        elif "invalid cvc" in result:
            response = "invalid_cvc 🚫"
        elif "stolen card" in result:
            response = "Stolen Card 🚫"
        elif "lost_card" in result:
            response = "Lost Card 🚫"
        elif "pickup_card" in result:
            response = "Pickup Card 🚫"
        elif "incorrect_number" in result:
            response = "Incorrect Card Number 🚫"
        elif "Your card has expired." in result or "expired_card" in result:
            response = "Expired Card 🚫"
        elif "intent_confirmation_challenge" in result:
            response = "Captcha 🚫"
        elif "Your card number is incorrect." in result:
            response = "Incorrect Card Number 🚫"
        elif (
            "Your card's expiration year is invalid." in result
            or "Your card's expiration year is invalid." in result
        ):
            response = "Expiration Year Invalid 🚫"
        elif (
            "Your card's expiration month is invalid." in result
            or "invalid_expiry_month" in result
        ):
            response = "Expiration Month Invalid 🚫"
        elif "card is not supported." in result:
            response = "Card Not Supported 🚫"
        elif "invalid account" in result:
            response = "Dead Card 🚫"
        elif (
            "Invalid API Key provided" in result
            or "testmode_charges_only" in result
            or "api_key_expired" in result
            or "Your account cannot currently make live charges." in result
        ):
            response = "stripe error contact support@stripe.com for more details 🚫"
        elif "Your card was declined." in result or "card was declined" in result:
            response = "Generic Decline 🚫"
        elif "Please Update Bearer Token" in result:
            response = "Token Expired Admin Has Been Notified 🚫"
        else:
            response = result + "🚫"
            with open("result_logs.txt", "a") as f:
                f.write(f"{result}\n")

        return response

    except Exception as e:
        response = f"{str(e)} 🚫"
        return response


async def authenticate(json, pk, session):
    try:
        three_d_secure_2_source = json["next_action"]["use_stripe_sdk"][
            "three_d_secure_2_source"
        ]
        url = "https://api.stripe.com/v1/3ds2/authenticate"
        data = {
            "source": three_d_secure_2_source,
            "browser": '{"fingerprintAttempted":false,"fingerprintData":null,"challengeWindowSize":null,"threeDSCompInd":"Y","browserJavaEnabled":false,"browserJavascriptEnabled":true,"browserLanguage":"en-US","browserColorDepth":"24","browserScreenHeight":"864","browserScreenWidth":"1536","browserTZ":"-360","browserUserAgent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/'
            + str(random.randint(115, 116))
            + '.0.0.0 Safari/537.36"}',
            "one_click_authn_device_support[hosted]": "false",
            "one_click_authn_device_support[same_origin_frame]": "false",
            "one_click_authn_device_support[spc_eligible]": "true",
            "one_click_authn_device_support[webauthn_eligible]": "true",
            "one_click_authn_device_support[publickey_credentials_get_allowed]": "true",
            "key": pk,
        }
        result = await session.post(url, data=data)

        try:
            return result.json()["state"]
        except:
            try:
                return result.json()["error"]["message"]
            except:
                return result.text

    except Exception as e:
        return e


async def one_click_3d_check(json, session):
    try:
        three_ds_method_url = json["next_action"]["use_stripe_sdk"][
            "three_ds_method_url"
        ]
        await session.get(three_ds_method_url)
    except Exception as e:
        pass

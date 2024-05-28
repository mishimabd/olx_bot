import asyncio
import json
import re
import asyncpg
import redis
import requests
from telegram import Update, Message, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackContext, Application, CommandHandler, MessageHandler, filters, \
    ConversationHandler

import utils

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

token_client = utils.get_token_client()
FIRST, SECOND, THIRD = range(3)


async def get_pool():
    return await asyncpg.create_pool(user='postgres', password='mishimabd',
                                     database='olx_bot', host='localhost')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    secret_key = context.user_data.get("selected_secret_key")
    if secret_key:
        await update.message.reply_text("Your selected key is: " + secret_key)
    else:
        await update.message.reply_text("You haven't selected any key yet.")


async def check_my_balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    token_auth = redis_client.get(f'access_token:{chat_id}')

    if token_auth:
        token_auth = token_auth.decode('utf-8')  # Decode the byte string to a standard string

        url = "https://www.olx.kz/api/partner/users/me/account-balance"
        headers = {
            "Authorization": f"Bearer {token_auth}",
            "Version": "2.0",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "PostmanRuntime/7.39.0",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive"
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            response_data = response.json()
            sum_amount = response_data["data"]["sum"]
            wallet_amount = response_data["data"]["wallet"]
            bonus_amount = response_data["data"]["bonus"]
            refund_amount = response_data["data"]["refund"]

            message = (
                f"Your balance details are as follows:\n"
                f"Sum: {sum_amount}\n"
                f"Wallet: {wallet_amount}\n"
                f"Bonus: {bonus_amount}\n"
                f"Refund: {refund_amount}"
            )

            await update.message.reply_text(message)
        elif response.status_code == 401:
            auth_url = (
                f"https://www.olx.kz/oauth/authorize/?client_id=200166&response_type=code&state=x93ld3v&scope=read+write+v2")
            await update.message.reply_text(
                f"You are not authorized. Please visit the following URL to authorize:\n{auth_url}")
        else:
            await update.message.reply_text(f"Error: {response.json()}")
    else:
        await update.message.reply_text("Authorization token not found. Please authenticate first.")


async def get_authenticated_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    token_auth = redis_client.get(f'access_token:{chat_id}')

    if token_auth:
        token_auth = token_auth.decode('utf-8')  # Decode the byte string to a standard string
        url = "https://www.olx.kz/api/partner/users/me"
        headers = {
            "Authorization": f"Bearer {token_auth}",
            "Content-Type": "application/json",
            "Version": "2.0"
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            user_data = response.json().get('data', {})
            user_name = user_data.get('name', 'N/A')
            user_email = user_data.get('email', 'N/A')
            user_status = user_data.get('status', 'N/A')
            created_at = user_data.get('created_at', 'N/A')
            last_login_at = user_data.get('last_login_at', 'N/A')

            message = (
                f"Your name is: {user_name}\n"
                f"Your email is: {user_email}\n"
                f"Account status: {user_status}\n"
                f"Account created at: {created_at}\n"
                f"Last login at: {last_login_at}"
            )
            await update.message.reply_text(message)
        else:
            await update.message.reply_text(f"Error: {response.status_code}")
    else:
        await update.message.reply_text("Authorization token not found. Please authenticate first.")


async def get_my_advertises(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    token_auth = redis_client.get(f'access_token:{chat_id}')

    if token_auth:
        token_auth = token_auth.decode('utf-8')  # Decode the byte string to a standard string
        url = "https://www.olx.kz/api/partner/adverts"
        headers = {
            "Authorization": f"Bearer {token_auth}",
            "Content-Type": "application/json",
            "Version": "2.0"
        }
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            ad_data = response.json().get('data', [])
            if ad_data:
                for ad in ad_data:
                    ad_title = ad.get('title', 'N/A')
                    ad_description = ad.get('description', 'N/A')
                    ad_price_value = ad.get('price', {}).get('value', 'N/A')
                    ad_price_currency = ad.get('price', {}).get('currency', 'N/A')
                    ad_category_id = ad.get('category_id', 'N/A')
                    ad_contact_name = ad.get('contact', {}).get('name', 'N/A')
                    ad_contact_phone = ad.get('contact', {}).get('phone', 'N/A')
                    ad_location_city_id = ad.get('location', {}).get('city_id', 'N/A')
                    ad_created_at = ad.get('created_at', 'N/A')
                    ad_valid_to = ad.get('valid_to', 'N/A')
                    ad_url = ad.get('url', 'N/A')

                    message = (
                        f"Ad Title: {ad_title}\n"
                        f"Description: {ad_description}\n"
                        f"Цена вашего объявления: {ad_price_value} {ad_price_currency}\n"
                        f"Category ID: {ad_category_id}\n"
                        f"Contact Name: {ad_contact_name}\n"
                        f"Contact Phone: {ad_contact_phone}\n"
                        f"City ID: {ad_location_city_id}\n"
                        f"Создано At: {ad_created_at}\n"
                        f"Valid To: {ad_valid_to}\n"
                        f"URL: {ad_url}\n"
                    )
                    await update.message.reply_text(message)
            else:
                await update.message.reply_text("No advertisements found.")
        else:
            await update.message.reply_text(f"Error: {response.status_code}")
    else:
        await update.message.reply_text("Authorization token not found. Please authenticate first.")


async def get_advert_statistics(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:  # This condition ensures the function handles messages
        chat_id = update.message.chat_id
        print("I am in advertise statistics")
        token_auth = redis_client.get(f'access_token:{chat_id}')
        if token_auth:
            token_auth = token_auth.decode('utf-8')  # Decode the byte string to a standard string
            url = "https://www.olx.kz/api/partner/adverts"
            headers = {
                "Authorization": f"Bearer {token_auth}",
                "Content-Type": "application/json",
                "Version": "2.0"
            }
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                ad_data = response.json().get('data', [])
                if ad_data:
                    keyboard = []
                    for ad in ad_data:
                        ad_id = ad.get('id', 'N/A')
                        ad_title = ad.get('title', 'N/A')
                        button = InlineKeyboardButton(ad_title, callback_data=f"select_advertise:{ad_id}")
                        keyboard.append([button])
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await update.message.reply_text("Select an advertisement:", reply_markup=reply_markup)
                else:
                    await update.message.reply_text("No advertisements found.")
            else:
                await update.message.reply_text(f"Error: {response.status_code}")
        else:
            await update.message.reply_text("Authorization token not found. Please authenticate first.")
    elif update.callback_query:  # This condition handles the callback queries
        query = update.callback_query
        await query.answer()

        chat_id = query.message.chat_id
        token_auth = redis_client.get(f'access_token:{chat_id}')
        if token_auth:
            token_auth = token_auth.decode('utf-8')  # Decode the byte string to a standard string
            ad_id = query.data.split(":")[1]
            url = f"https://www.olx.kz/api/partner/adverts/{ad_id}/statistics"
            headers = {
                "Authorization": f"Bearer {token_auth}",
                "Content-Type": "application/json",
                "Version": "2.0"
            }
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                stats_data = response.json()
                # Format and send the statistics data
                stats_message = f"Statistics for ad {ad_id}:\n\n{stats_data}"
                await query.message.reply_text(stats_message)
            else:
                await query.message.reply_text(f"Error retrieving statistics: {response.status_code}")
        else:
            await query.message.reply_text("Authorization token not found. Please authenticate first.")
async def validate_advert(title, description):
    invalid_pattern = r"(.)\1\1"
    if re.search(invalid_pattern, title) or re.search(invalid_pattern, description):
        return False, "Title or description contains invalid repeating characters."

    # Check for capital letters count
    def capital_letter_ratio(text):
        return sum(1 for c in text if c.isupper()) / len(text)

    if capital_letter_ratio(title) > 0.5 or capital_letter_ratio(description) > 0.5:
        return False, "Title or description contains more than 50% capital letters."

    # Check title length
    if not (16 <= len(title) <= 70):
        return False, "Title must be between 16 and 70 characters long."

    # Check description length
    if not (80 <= len(description) <= 9000):
        return False, "Description must be between 80 and 9000 characters long."

    # Check for email addresses and phone numbers
    email_pattern = r'\S+@\S+\.\S+'
    phone_pattern = r'\+?\d[\d\s-]{7,}\d'
    if re.search(email_pattern, title) or re.search(email_pattern, description):
        return False, "Title or description contains an email address."
    if re.search(phone_pattern, title) or re.search(phone_pattern, description):
        return False, "Title or description contains a phone number."

    return True, "Validation passed."


async def create_adv(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    token_auth = redis_client.get(f'access_token:{chat_id}')

    if token_auth:
        token_auth = token_auth.decode('utf-8')
        data = {
            "title": context.user_data['title'],
            "description": context.user_data['description'],
            "category_id": 1459,
            "advertiser_type": "private",
            "contact": {
                "name": 'mishima_test',
                "phone": 8876178672
            },
            "location": {
                "city_id": 1671, "latitude": 45.45172, "longitude": 79.97816
            },
            "price": {
                "value": context.user_data['price']
            },
            "attributes": [
                {
                    "code": "state",
                    "value": "used"
                },
                {
                    "code": "brand",
                    "value": "yokohama"
                },
                {
                    "code": "diameter_inches",
                    "value": "15"
                },
                {
                    "code": "quantity",
                    "value": "set_of_4_tires"
                }
            ]
        }

        url = "https://www.olx.kz/api/partner/adverts"
        headers = {
            "Authorization": f"Bearer {token_auth}",
            "Version": "2.0",
            "Content-Type": "application/json",
            "User-Agent": "PostmanRuntime/7.39.0",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive"
        }

        # Send the POST request with JSON data
        response = requests.post(url, headers=headers, json=data)
        data = response.json()
        if response.json().get("error"):
            await context.bot.send_message(chat_id, response.json())
        else:
            advert_url = data['data']['url']
            await context.bot.send_message(chat_id, f"Advert created successfully. Your advert link is: {advert_url}")


    else:
        await context.bot.send_message(chat_id, "Authorization token not found. Please authenticate first.")


async def start(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text('Please enter the title of advertise:')
    return FIRST


async def first_argument(update: Update, context: CallbackContext) -> int:
    context.user_data['title'] = update.message.text
    await update.message.reply_text('Please enter the details of advertise:')
    return SECOND


async def second_argument(update: Update, context: CallbackContext) -> int:
    context.user_data['description'] = update.message.text
    await update.message.reply_text('Please enter the price of advertise:')
    return THIRD


async def third_argument(update: Update, context: CallbackContext) -> int:
    context.user_data['price'] = update.message.text

    await create_adv(update, context)

    # End conversation
    return ConversationHandler.END


async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text('Operation cancelled.')
    return ConversationHandler.END

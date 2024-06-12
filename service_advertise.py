import asyncio
import base64
import logging
import os
from datetime import datetime, timedelta
import pandas as pd
import asyncpg
import redis
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from telegram import Update, Message, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackContext, Application, CommandHandler, MessageHandler, filters, \
    ConversationHandler

import utils
scheduler = BackgroundScheduler()
scheduler.start()
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

token_client = utils.get_token_client()

FIRST, SECOND, THIRD, FOURTH, FIFTH,SIXTH, DATETIME = range(7)
FILE = range(1)

async def get_pool():
    return await asyncpg.create_pool(user='postgres', password='mishimabd',
                                     database='olx_bot', host='localhost')


def run_async(coroutine, *args):
    # Create a new event loop for this thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        # Run the coroutine in the new event loop
        loop.run_until_complete(coroutine(*args))
    finally:
        # Close the event loop when done
        loop.close()


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
                f"Ваши детали баланса следующие:\n"
                f"Сумма: {sum_amount}\n"
                f"Кошелек: {wallet_amount}\n"
                f"Бонус: {bonus_amount}\n"
                f"Возврат: {refund_amount}"
            )

            await update.message.reply_text(message)
        elif response.status_code == 401:
            auth_url = (
                f"https://www.olx.kz/oauth/authorize/?client_id=200166&response_type=code&state=x93ld3v&scope=read&redirect_uri=https://185.4.180.8"
                f"+write+v2")
            await update.message.reply_text(
                f"Вы не авторизованы. Пожалуйста перейдите по ссылке:\n{auth_url}")
        else:
            await update.message.reply_text(f"Error: {response.json()}")
    else:
        auth_url = (
            f"https://www.olx.kz/oauth/authorize/?client_id=200166&response_type=code&state=x93ld3v&scope=read&redirect_uri=https://185.4.180.8"
            f"+write+v2")
        await update.message.reply_text(
                f"Вы не авторизованы. Пожалуйста перейдите по ссылке:\n{auth_url}")


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
                f"Ваше имя: {user_name}\n"
                f"Ваш email: {user_email}\n"
                f"Статус аккаунта: {user_status}\n"
                f"Аккаунт создан: {created_at}\n"
                f"Последний вход: {last_login_at}"
            )
            await update.message.reply_text(message)
        elif response.status_code == 401:
            auth_url = (
                f"https://www.olx.kz/oauth/authorize/?client_id=200166&response_type=code&state=x93ld3v&scope=read"
                f"+write+v2")
            await update.message.reply_text(
                f"Вы не авторизованы. Пожалуйста перейдите по ссылке:\n{auth_url}")
        else:
            await update.message.reply_text(f"Error: {response.status_code}")
    else:
        auth_url = (
            f"https://www.olx.kz/oauth/authorize/?client_id=200166&response_type=code&state=x93ld3v&scope=read"
            f"+write+v2")
        await update.message.reply_text(
                f"Вы не авторизованы. Пожалуйста перейдите по ссылке:\n{auth_url}")


async def get_my_advertises(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    token_auth = redis_client.get(f'access_token:{chat_id}')
    print(token_auth)
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
                active_ads = [ad for ad in ad_data if ad.get('status') == 'active']
                if active_ads:
                    for ad in active_ads:
                        ad_title = ad.get('title', 'N/A')
                        ad_description = ad.get('description', 'N/A')
                        ad_price_value = ad.get('price', {}).get('value', 'N/A')
                        ad_price_currency = ad.get('price', {}).get('currency', 'N/A')
                        ad_contact_name = ad.get('contact', {}).get('name', 'N/A')
                        ad_created_at = ad.get('created_at', 'N/A')
                        ad_valid_to = ad.get('valid_to', 'N/A')
                        ad_url = ad.get('url', 'N/A')

                        images = ad.get('images', [])
                        ad_image_url = images[0].get('url', '') if images else ''

                        message = (
                            f"Название: {ad_title}\n"
                            f"Описание: {ad_description}\n"
                            f"Цена вашего объявления: {ad_price_value} {ad_price_currency}\n"
                            f"Автор объявления: {ad_contact_name}\n"
                            f"Создано: {ad_created_at}\n"
                            f"Срок до: {ad_valid_to}\n"
                            f"Ссылка: {ad_url}\n"
                        )

                        if ad_image_url:
                            image_response = requests.get(ad_image_url)
                            if image_response.status_code == 200:
                                await context.bot.send_photo(chat_id=chat_id, photo=image_response.content, caption=message)
                            else:
                                await update.message.reply_text("Failed to load image, here are the details:\n" + message)
                        else:
                            await update.message.reply_text("Нет картинки\n" + message)
                else:
                    await update.message.reply_text("Активные объявления не найдены.")
            else:
                await update.message.reply_text("Не найдено.")
        elif response.status_code == 401:
            auth_url = (
                f"https://www.olx.kz/oauth/authorize/?client_id=200166&response_type=code&state=x93ld3v&scope=read"
                f"+write+v2")
            await update.message.reply_text(
                f"Вы не авторизованы. Пожалуйста перейдите по ссылке:\n{auth_url}")
        else:
            await update.message.reply_text(f"Error: {response.status_code}")
    else:
        auth_url = (
            f"https://www.olx.kz/oauth/authorize/?client_id=200166&response_type=code&state=x93ld3v&scope=read"
            f"+write+v2")
        await update.message.reply_text(
                f"Вы не авторизованы. Пожалуйста перейдите по ссылке:\n{auth_url}")

async def billing_history(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    token_auth = redis_client.get(f'access_token:{chat_id}')

    if token_auth:
        token_auth = token_auth.decode('utf-8')  # Decode the byte string to a standard string

        url = "https://www.olx.kz/api/partner/users/me/billing"
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
            billing_entries = response_data.get('data', [])

            if billing_entries:
                message = "История биллинга:\n\n"
                for entry in billing_entries:
                    date = entry.get('date', 'N/A')
                    formatted_date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S').strftime('%d-%m-%Y %H:%M:%S')
                    message += (
                        f"Название: {entry.get('name', 'N/A')}\n"
                        f"Дата: {formatted_date}\n"
                        f"Цена: {entry.get('price', 'N/A')}\n\n"
                    )
            else:
                message = "История биллинга пуста."

            await update.message.reply_text(message)

        elif response.status_code == 401:
            auth_url = (
                f"https://www.olx.kz/oauth/authorize/?client_id=200166&response_type=code&state=x93ld3v&scope=read"
                f"+write+v2")
            await update.message.reply_text(
                f"Вы не авторизованы. Пожалуйста, перейдите по ссылке:\n{auth_url}")
        else:
            await update.message.reply_text(f"Ошибка: {response.json().get('message', 'Неизвестная ошибка')}")

    else:
        auth_url = (
            f"https://www.olx.kz/oauth/authorize/?client_id=200166&response_type=code&state=x93ld3v&scope=read"
            f"+write+v2")
        await update.message.reply_text(
            f"Вы не авторизованы. Пожалуйста, перейдите по ссылке:\n{auth_url}")


async def packets_left(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    token_auth = redis_client.get(f'access_token:{chat_id}')

    if token_auth:
        token_auth = token_auth.decode('utf-8')  # Decode the byte string to a standard string

        url = "https://www.olx.kz/api/partner/users/me/packets"
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
            packets_data = response_data.get('data', [])

            if packets_data:
                message = "Оставшиеся пакеты:\n\n"
                for packet in packets_data:
                    message += (
                        f"Название пакета: {packet.get('name', 'N/A')}\n"
                        f"Осталось размещений: {packet.get('left', 'N/A')}\n"
                        f"Активен до: {packet.get('active_to', 'N/A')}\n\n"
                    )
            else:
                message = "Нет активных пакетов."

            await update.message.reply_text(message)

        elif response.status_code == 401:
            auth_url = (
                f"https://www.olx.kz/oauth/authorize/?client_id=200166&response_type=code&state=x93ld3v&scope=read"
                f"+write+v2")
            await update.message.reply_text(
                f"Вы не авторизованы. Пожалуйста, перейдите по ссылке:\n{auth_url}")
        else:
            await update.message.reply_text(f"Ошибка: {response.json().get('message', 'Неизвестная ошибка')}")

    else:
        auth_url = (
            f"https://www.olx.kz/oauth/authorize/?client_id=200166&response_type=code&state=x93ld3v&scope=read"
            f"+write+v2")
        await update.message.reply_text(
            f"Вы не авторизованы. Пожалуйста, перейдите по ссылке:\n{auth_url}")


def check_advertises(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_ids = redis_client.keys('access_token:*')
    for chat_id_key in chat_ids:
        chat_id = chat_id_key.split(b':')[1].decode('utf-8')
        token_auth = redis_client.get(chat_id_key)
        if token_auth:
            token_auth = token_auth.decode('utf-8')
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
                        ad_valid_to = ad.get('valid_to', 'N/A')
                        ad_valid_to_dt = datetime.strptime(ad_valid_to, '%Y-%m-%d %H:%M:%S')
                        if datetime.now(ad_valid_to_dt.tzinfo) + timedelta(days=20) >= ad_valid_to_dt:
                            message = (
                                f"Айди: {ad.get('id', 'N/A')}\n"
                                f"Название: {ad.get('title', 'N/A')}\n"
                                f"Описание: {ad.get('description', 'N/A')}\n"
                                f"Срок до: {ad_valid_to}\n"
                                f"Ссылка: {ad.get('url', 'N/A')}\n"
                            )
                            logging.info(message)
                            advert_id = ad.get('id', 'N/A')
                            if advert_id != 'N/A':
                                # post_url = f"https://www.olx.kz/api/partner/adverts/{advert_id}/paid-features"
                                # post_body = {
                                #     "payment_method": "account",
                                #     "code": "pushup"
                                # }
                                # post_response = requests.post(post_url, headers=headers, json=post_body)
                                # print(post_response.json())
                                # if post_response.status_code == 200:
                                #     logging.info(f"Successfully sent paid feature request for advert ID: {advert_id}")
                                # else:
                                #     logging.error(
                                #         f"Failed to send paid feature request for advert ID: {advert_id}, status code: {post_response.status_code}")
                                post_url = f"https://www.olx.kz/api/partner/adverts/{advert_id}/commands"
                                post_body = {
                                    "command": "refresh"
                                }
                                post_response = requests.post(post_url, headers=headers, json=post_body)
                                print(post_response.json())
                                if post_response.status_code == 200:
                                    logging.info(f"Successfully refreshed advert ID: {advert_id}")
                                else:
                                    logging.error(
                                        f"Failed to send paid feature request for advert ID: {advert_id}, status code: {post_response.status_code}")
            else:
                print(f"Failed to fetch ads for chat_id: {chat_id}, status code: {response.status_code}")


async def get_statistic_for_advertise(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
                # Collect titles and IDs
                ad_titles_ids = [(ad.get('title', 'N/A'), ad.get('id', 'N/A')) for ad in ad_data]

                # Create buttons for each title
                buttons = [
                    [InlineKeyboardButton(title, callback_data=str(ad_id))]
                    for title, ad_id in ad_titles_ids
                ]

                # Create InlineKeyboardMarkup from buttons
                reply_markup = InlineKeyboardMarkup(buttons)

                # Send the message with all buttons
                await update.message.reply_text("Выберите объявление:", reply_markup=reply_markup)
            else:
                await update.message.reply_text("No advertisements found.")
        elif response.status_code == 401:
            auth_url = (
                f"https://www.olx.kz/oauth/authorize/?client_id=200166&response_type=code&state=x93ld3v&scope=read"
                f"+write+v2")
            await update.message.reply_text(
                f"Вы не авторизованы. Пожалуйста перейдите по ссылке:\n{auth_url}")
        else:
            await update.message.reply_text(f"Error: {response.status_code}")
    else:
        auth_url = (
            f"https://www.olx.kz/oauth/authorize/?client_id=200166&response_type=code&state=x93ld3v&scope=read"
            f"+write+v2")
        await update.message.reply_text(
                f"Вы не авторизованы. Пожалуйста перейдите по ссылке:\n{auth_url}")


async def get_statistic(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    chat_id = query.message.chat_id
    token_auth = redis_client.get(f'access_token:{chat_id}')
    token_auth = token_auth.decode('utf-8')  # Decode the byte string to a standard string

    # Extracting the ad_id from the callback data
    ad_id = query.data

    url = f"https://www.olx.kz/api/partner/adverts/{ad_id}/statistics"
    headers = {
        "Authorization": f"Bearer {token_auth}",
        "Content-Type": "application/json",
        "Version": "2.0"
    }
    response = requests.get(url, headers=headers)
    print(response.json())
    # Parsing the response into a readable format
    data = response.json().get('data', {})
    advert_views = data.get('advert_views', 0)
    phone_views = data.get('phone_views', 0)
    users_observing = data.get('users_observing', 0)

    # Constructing the reply message
    message = (
        f"Просмотры объявления: {advert_views}\n"
        f"Просмотры телефона: {phone_views}\n"
        f"Пользователи, отслеживающие объявление: {users_observing}"
    )

    await query.message.reply_text(message)


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
                "city_id": 1,
                "district_id": 1
            },
            "price": {
                "value": context.user_data['price']
            },
            "images": [
                {
                    "url": context.user_data['image_url']
                }
            ],
            "attributes": [
                {
                    "code": "state",
                    "value": context.user_data['state']
                },
                {
                    "code": "brand",
                    "value": "yokohama"
                },
                {
                    "code": "diameter_inches",
                    "value": context.user_data['diameter_inches']
                },
                {
                    "code": "quantity",
                    "value": "set_of_4_tires"
                }
            ]
        }
        print(data)
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
            print(response.json())
            await context.bot.send_message(chat_id, response.json())
        else:
            advert_url = data['data']['url']
            await context.bot.send_message(chat_id, f"Advert created successfully. Your advert link is: {advert_url}")
    else:
        auth_url = (
            f"https://www.olx.kz/oauth/authorize/?client_id=200166&response_type=code&state=x93ld3v&scope=read"
            f"+write+v2")
        await update.message.reply_text(
                f"Вы не авторизованы. Пожалуйста перейдите по ссылке:\n{auth_url}")


async def create_advertises_by_excel(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    token_auth = redis_client.get(f'access_token:{chat_id}')

    if not token_auth:
        auth_url = (
            f"https://www.olx.kz/oauth/authorize/?client_id=200166&response_type=code&state=x93ld3v&scope=read"
            f"+write+v2")
        await update.message.reply_text(f"Вы не авторизованы. Пожалуйста перейдите по ссылке:\n{auth_url}")
        return
    await update.message.reply_text("Пожалуйста, отправьте файл Excel с данными объявлений.")
    return FILE


async def handle_excel_file(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    token_auth = redis_client.get(f'access_token:{chat_id}')
    token_auth = token_auth.decode('utf-8')
    file = await update.message.document.get_file()
    file_path = f"downloads/{file.file_id}.xlsx"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    await file.download_to_drive(file_path)

    df = pd.read_excel(file_path)
    os.remove(file_path)

    for index, row in df.iterrows():
        combined_description = f"{row['Название']}\n\n{row['Описание']}"
        data = {
            "title": row['Название'],
            "description": combined_description,
            "category_id": 1459,
            "advertiser_type": "business",
            "contact": {
                "name": 'mishima_test',
                "phone": 8876178672
            },
            "location": {
                "city_id": 1,
                "district_id": 1
            },
            "price": {
                "value": row['Цена']
            },
            "images": [
                {
                    "url": row['Ссылка на картинку']
                }
            ],
            "attributes": [
                {
                    "code": "state",
                    "value": row['Состояние']
                },
                {
                    "code": "brand",
                    "value": row['Бренд производителя']
                },
                {
                    "code": "diameter_inches",
                    "value": row['Диаметр, дюймы']
                },
                {
                    "code": "profile_width_mm",
                    "value": row['Ширина профиля, мм']
                },
                {
                    "code": "seasonality",
                    "value": row['Сезонность']
                },
                {
                    "code": "thorns",
                    "value": row['Шипы']
                },
                {
                    "code": "profile_height",
                    "value": row['Высота профиля, %']
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
            print(response.json())
            await context.bot.send_message(chat_id, response.json())
        else:
            advert_url = data['data']['url']
            await context.bot.send_message(chat_id, f"Объявление создано успешно! Ваша ссылка на объявление: {advert_url}")


async def start(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text('Пожалуйста, введите название объявления:')
    return FIRST


async def first_argument(update: Update, context: CallbackContext) -> int:
    context.user_data['title'] = update.message.text
    await update.message.reply_text('Пожалуйста, введите описание объявления:')
    return SECOND


async def second_argument(update: Update, context: CallbackContext) -> int:
    context.user_data['description'] = update.message.text
    await update.message.reply_text('Пожалуйста, введите цену объявления:')
    return THIRD


async def third_argument(update: Update, context: CallbackContext) -> int:
    context.user_data['price'] = update.message.text
    await update.message.reply_text('Напишите состояние колес\nНовые - new:\nИспользованные - used:')
    return FOURTH


async def fourth_argument(update: Update, context: CallbackContext) -> int:
    context.user_data['state'] = update.message.text
    await update.message.reply_text('Введите диаметр шины:')
    return FIFTH


async def fifth_argument(update: Update, context: CallbackContext) -> int:
    context.user_data['diameter_inches'] = update.message.text
    await update.message.reply_text('Пожалуйста, отправьте фотографию товара:')
    return SIXTH


async def sixth_argument(update: Update, context: CallbackContext) -> int:
    photo = update.message.photo[-1]
    photo_file = await photo.get_file()

    # Define a local file path to save the image
    file_path = f"downloads/{photo.file_id}.jpg"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Download the file to the specified path
    await photo_file.download_to_drive(file_path)

    # Upload the image to ImgBB and get the URL
    image_url = upload_to_imgbb(file_path)
    context.user_data['image_url'] = image_url

    # Clean up the downloaded file
    os.remove(file_path)

    await update.message.reply_text('Пожалуйста, укажите дату и время публикации в формате ДД.ММ.ГГГГ ЧЧ:ММ.')
    return DATETIME


async def schedule_publication(update: Update, context: CallbackContext) -> int:
    publication_time = update.message.text
    try:
        scheduled_time = datetime.strptime(publication_time, '%d.%m.%Y %H:%M')
        context.user_data['scheduled_time'] = scheduled_time

        # Schedule the job
        trigger = DateTrigger(run_date=scheduled_time)
        scheduler.add_job(run_async, trigger, args=[create_adv, update, context])

        await update.message.reply_text(f"Объявление запланировано на {scheduled_time}.")
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("Неправильный формат даты и времени. Пожалуйста, используйте ДД.ММ.ГГГГ ЧЧ:ММ.")
        return DATETIME


def upload_to_imgbb(file_path):
    imgbb_api_key = '9ecf9d1a3564cf1edf1060c69eebd34f'
    with open(file_path, 'rb') as file:
        # Read the binary file and encode it as base64
        encoded_image = base64.b64encode(file.read()).decode('utf-8')

    response = requests.post(
        'https://api.imgbb.com/1/upload',
        data={
            'key': imgbb_api_key,
            'image': encoded_image,
        }
    )
    response_data = response.json()
    if response.status_code == 200:
        return response_data['data']['url']
    else:
        raise Exception(f"Failed to upload image: {response_data}")


async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text('Operation cancelled.')
    return ConversationHandler.END

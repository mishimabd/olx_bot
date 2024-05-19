import asyncpg
import requests
from telegram import Update
from telegram.ext import ContextTypes, CallbackContext

import utils

token_auth = utils.get_token_auth()
token_client = utils.get_token_client()


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
    url = "https://www.olx.kz/api/users/me/account-balance"
    headers = {
        "Authorization": f"Bearer {token_auth}",
        "Version": "2.0",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "PostmanRuntime/7.39.0",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive"
    }
    print(headers)
    response = requests.get(url, headers=headers)
    await update.message.reply_text(response.text)
    print(response.json())
    if response.status_code == 200:
        await update.message.reply_text(response.text)
    else:
        return f"Error: {response.status_code}"


async def get_authenticated_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    secret_key = context.user_data.get("selected_secret_key")  # Use get() method to handle absence of key gracefully
    if secret_key:
        url = "https://www.olx.kz/api/users/me"
        headers = {
            "Authorization": f"Bearer {token_auth}",
            "Content-Type": "application/json",
            "Version": "2.0"
        }

        response = requests.get(url, headers=headers)
        await update.message.reply_text(response.text)
        if response.status_code == 200:
            await update.message.reply_text(response.text)
        else:
            return f"Error: {response.status_code}"
    else:
        await update.message.reply_text("You haven't selected any key yet.")


async def get_advert_statistics(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    secret_key = context.user_data.get("selected_secret_key")
    advert_id = "advert_id"
    if secret_key:
        url = "https://www.olx.kz/api/partner/adverts/" + advert_id + "/statistics"
        headers = {
            "Authorization": f"Bearer {secret_key}",
            "Content-Type": "application/json",
            "Version": "2.0"
        }

        response = requests.get(url, headers=headers)
        await update.message.reply_text(response.text)
        if response.status_code == 200:
            await update.message.reply_text(response.text)
        else:
            print("u are cool")
            return f"Error: {response.status_code}"
    else:
        await update.message.reply_text("You haven't selected any key yet.")


async def get_my_advertises(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    secret_key = context.user_data.get("selected_secret_key")
    if secret_key:
        url = "https://www.olx.kz/api/partner/adverts"
        print("I AM HERER")
        response = requests.get(url)
        await update.message.reply_text(response.text)
        if response.status_code == 200:
            await update.message.reply_text(response.text)
        else:
            print("u are cool")
            return f"Error: {response.status_code}"
    else:
        await update.message.reply_text("You haven't selected any key yet.")

import asyncpg
from telegram import Update
from telegram.ext import CallbackContext
from service_advertise import (get_advert_statistics,get_authenticated_user,
                               check_my_balance, get_my_advertises)
from buttons import advertise_buttons, secret_settings_buttons, start_button, olx_api_buttons
from service_secret_key import get_secret_keys, add_secret_key, save_secret_key


async def get_pool():
    return await asyncpg.create_pool(user='postgres', password='mishimabd',
                                     database='olx_bot', host='localhost')


async def input_data(update: Update, context: CallbackContext) -> None:
    if context.user_data["is_text_for_adding"]:
        user_id = update.message.from_user.id
        secret_key = update.message.text
        pool = await get_pool()
        async with pool.acquire() as connection:
            await connection.execute("INSERT INTO user_secret_keys (telegram_user_id, secret_key) VALUES ($1, $2)",
                                     str(user_id), secret_key)
        context.user_data["selected_secret_key"] = secret_key
        await update.message.reply_text("Secret key has been added successfully!")
        context.user_data["is_text_for_adding"] = False
    else:
        await update.message.reply_text("I didn't understand(")


async def handle_action_settings(update: Update, context: CallbackContext) -> None:
    user_choice = update.message.text
    if user_choice == "Add secret key":
        await add_secret_key(update, context)
    elif user_choice == "Get list of my secret keys":
        await get_secret_keys(update, context)
    elif user_choice == "Обратно в главную":
        await start_button(update, context)


async def handle_action_advertises(update: Update, context: CallbackContext) -> None:
    user_choice = update.message.text
    if user_choice == "Get my advertises":
        await get_my_advertises(update, context)
    elif user_choice == "Get advert statistics":
        await get_advert_statistics(update, context)
    elif user_choice == "Update my advertise":
        await get_authenticated_user(update, context)
    elif user_choice == "Обратно в главную":
        await start_button(update, context)


async def handle_action_main(update: Update, context: CallbackContext) -> None:
    user_choice = update.message.text
    if user_choice == "OLX API":
        await olx_api_buttons(update, context)
    elif user_choice == "Secret Key Settings":
        await secret_settings_buttons(update, context)


async def handle_action_olx_api(update: Update, context: CallbackContext) -> None:
    user_choice = update.message.text
    if user_choice == "Advertises":
        await advertise_buttons(update, context)
    elif user_choice == "My balance":
        await check_my_balance(update, context)

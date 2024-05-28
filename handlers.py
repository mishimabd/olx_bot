import asyncpg
from telegram import Update
from telegram.ext import CallbackContext
from service_advertise import (get_advert_statistics,get_authenticated_user,
                               check_my_balance, get_my_advertises, create_adv)
from buttons import advertise_buttons, secret_settings_buttons, start_button, olx_api_buttons
from service_secret_key import get_secret_keys, add_secret_key, save_secret_key


async def get_pool():
    return await asyncpg.create_pool(user='postgres', password='mishimabd',
                                     database='olx_bot', host='localhost')


async def input_data(update: Update, context: CallbackContext) -> None:
    # Check if the message contains photos
    if update.message.photo:
        # Get the list of photo sizes
        photo_sizes = update.message.photo
        # Get the last (largest) photo size
        largest_photo = photo_sizes[-1]
        # Get the file ID of the largest photo
        file_id = largest_photo.file_id
        # Request file path using getFile method
        file_path = await context.bot.get_file(file_id)
        # Construct URL for accessing the photo
        photo_url = f"https://api.telegram.org/file/bot{context.bot.token}/{file_path}"
        # Now you can use photo_url to access the photo
        print("Photo URL:", photo_url)
        # Do whatever you need with the photo URL

        # Example: Reply to the user with the photo URL
        await update.message.reply_text(f"Here is the URL of your photo: {photo_url}")
    else:
        await update.message.reply_text("Please send a photo.")


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
    elif user_choice == "Get Advertise Statistics":
        await get_advert_statistics(update, context)
    elif user_choice == "Get User Information":
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

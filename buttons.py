import requests
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, MessageHandler, CommandHandler, filters, CallbackContext

TELEGRAM_BOT_TOKEN = "7051155336:AAEGyPRtiNELXFL5t2i2DNI5lRhLRJeSQMo"

async def advertise_buttons(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    buttons = [
        [KeyboardButton("Get my advertises")],
        [KeyboardButton("Get advert statistics")],
        [KeyboardButton("Update my advertise")],
        [KeyboardButton("Обратно в главную")]
    ]
    reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    await update.message.reply_text(
        f"Привет, {user.first_name}! Здесь вы можете продвигать свои рекламы на Olx.kz. Выберите действие:",
        reply_markup=reply_markup
    )


async def secret_settings_buttons(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    buttons = [
        [KeyboardButton("Get list of my secret keys")],
        [KeyboardButton("Add secret key")],
        [KeyboardButton("Обратно в главную")]
    ]
    reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    await update.message.reply_text(
        f"{user.first_name}, это настройки секретного ключа на платформе Olx Developers. Выберите действие:",
        reply_markup=reply_markup
    )


async def start_button(update: Update, context: CallbackContext) -> None:
    auth_url = (f"https://www.olx.kz/oauth/authorize/"
                f"?client_id=200166"
                f"&response_type=code"
                f"&scope=read+write+v2"
                f"&redirect_uri=http://127.0.0.1:5000")
    await update.message.reply_text(f"Please visit the following URL to authorize:\n{auth_url}")
    context.user_data["is_text_for_adding"] = False
    user = update.message.from_user
    buttons = [
        [KeyboardButton("OLX API")],
        [KeyboardButton("Secret Key Settings")]
    ]
    print(context.user_data["is_text_for_adding"])
    reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    await update.message.reply_text(
        f"Привет, {user.first_name}! Я бот для размещения рекламы на Olx.kz. Выберите действие:",
        reply_markup=reply_markup
    )


async def olx_api_buttons(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    buttons = [
        [KeyboardButton("Advertises")],
        [KeyboardButton("My balance")],
        [KeyboardButton("Обратно в главную")]
    ]
    reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    await update.message.reply_text(
        f"{user.first_name}, это Olx Developers. Выберите действие:",
        reply_markup=reply_markup
    )
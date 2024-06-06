import requests
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, MessageHandler, CommandHandler, filters, CallbackContext

TELEGRAM_BOT_TOKEN = "7051155336:AAEGyPRtiNELXFL5t2i2DNI5lRhLRJeSQMo"

async def advertise_buttons(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    buttons = [
        [KeyboardButton("Все объявления")],
        [KeyboardButton("Создать объявление")],
        [KeyboardButton("Создать объявления по файлу")],
        [KeyboardButton("Статистика")],
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
    context.user_data["is_text_for_adding"] = False
    user = update.message.from_user
    buttons = [
        [KeyboardButton("OLX API")],
        [KeyboardButton("Информация про пользователя")]
    ]

    reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    await update.message.reply_text(
        f"Привет, {user.first_name}! Я бот для размещения рекламы на Olx.kz. Выберите действие:",
        reply_markup=reply_markup
    )


async def olx_api_buttons(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    buttons = [
        [KeyboardButton("Объявления")],
        [KeyboardButton("История затрат")],
        [KeyboardButton("Остаток пакетов")],
        [KeyboardButton("Мой баланс")],
        [KeyboardButton("Обратно в главную")]
    ]
    reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    await update.message.reply_text(
        f"{user.first_name}, это Olx Developers. Выберите действие:",
        reply_markup=reply_markup
    )
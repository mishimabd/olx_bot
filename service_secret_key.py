import asyncpg
import requests
from aiogram import types
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram import Update
from telegram.ext import ContextTypes, CallbackContext


async def get_pool():
    return await asyncpg.create_pool(user='postgres', password='mishimabd',
                                     database='olx_bot', host='localhost')


async def get_secret_keys(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    pool = await get_pool()
    async with pool.acquire() as connection:
        secret_keys = await connection.fetch("SELECT secret_key FROM user_secret_keys WHERE telegram_user_id = $1",
                                             str(user_id))

    if secret_keys:
        keyboard = [[InlineKeyboardButton(secret_key['secret_key'], callback_data=secret_key['secret_key'])] for
                    secret_key in secret_keys]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Choose a secret key:",
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text("You haven't added any secret keys yet.")


async def add_secret_key(update: Update, context: CallbackContext) -> None:
    context.user_data["is_text_for_adding"] = True
    await update.message.reply_text("Please, write your secret key")


async def save_secret_key(update: Update, context: CallbackContext) -> None:
    query: types.CallbackQuery = update.callback_query
    secret_key = query.data
    context.user_data['selected_secret_key'] = secret_key
    await query.message.reply_text(f"You've selected {secret_key}.")


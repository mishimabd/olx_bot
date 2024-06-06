import requests
from telegram import Update, Message, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackContext, Application, CommandHandler, MessageHandler, filters, \
    ConversationHandler
import redis
import utils

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

token_client = utils.get_token_client()


async def get_paid_features(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    token_auth = redis_client.get(f'access_token:{chat_id}')

    if token_auth:
        token_auth = token_auth.decode('utf-8')  # Decode the byte string to a standard string
        url = "https://www.olx.kz/api/partner/paid-features"
        headers = {
            "Authorization": f"Bearer {token_auth}",
            "Content-Type": "application/json",
            "Version": "2.0"
        }
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json().get('data', [])

            if data:
                message = "Available Promotional Services:\n\n"
                for service in data:
                    code = service.get('code', 'N/A')
                    service_type = service.get('type', 'N/A')
                    duration = service.get('duration', 'N/A')
                    name = service.get('name', 'N/A')
                    message += (
                        f"Name: {name}\n"
                        f"Code: {code}\n"
                        f"Type: {service_type}\n"
                        f"Duration: {duration} days\n\n"
                    )
                await update.message.reply_text(message)
            else:
                await update.message.reply_text("No paid features found.")
        elif response.status_code == 401:
            auth_url = (
                f"https://www.olx.kz/oauth/authorize/?client_id=200166&response_type=code&state=x93ld3v&scope=read"
                f"+write+v2")
            await update.message.reply_text(
                f"You are not authorized. Please visit the following URL to authorize:\n{auth_url}")
        else:
            await update.message.reply_text(f"Error: {response.status_code}")
    else:
        await update.message.reply_text("Authorization token not found. Please authenticate first.")

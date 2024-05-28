from flask import Flask, request, Blueprint
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, \
    ConversationHandler, filters
import requests
import logging
from threading import Thread
import redis
from service_advertise import create_adv, first_argument, second_argument, third_argument, cancel, start, get_advert_statistics
# Import your handlers and buttons
from handlers import (input_data, handle_action_settings, handle_action_main, save_secret_key, handle_action_advertises,
                      handle_action_olx_api)
from buttons import start_button

FIRST, SECOND, THIRD = range(3)
# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

CLIENT_ID = "200166"
CLIENT_SECRET = "Km1wN26hPhRaMhHkCGtLW8EjvPkLMn6Kwr10EhzrPci5NWot"
TOKEN_URL = "https://www.olx.kz/api/open/oauth/token"
AUTH_URL = "https://www.olx.kz/oauth/authorize/"
TELEGRAM_BOT_TOKEN = "7051155336:AAEGyPRtiNELXFL5t2i2DNI5lRhLRJeSQMo"

# Initialize Redis client
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

# Initialize Flask app and blueprint
app = Flask(__name__)
oauth_blueprint = Blueprint('oauth', __name__)


# Route for OAuth 2.0 callback
@oauth_blueprint.route('/')
def oauth_callback():
    code = request.args.get('code')
    chat_id = request.args.get('state')

    if code and chat_id:
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
        }
        print(data)
        response = requests.post(TOKEN_URL, data=data)

        if response.status_code == 200:
            try:
                token_response = response.json()
                access_token = token_response.get('access_token')

                if access_token:
                    print(chat_id)
                    redis_client.set('access_token:1924374737', access_token)
                    application.bot.send_message(chat_id, f'Authorization successful! Access token: {access_token}')
                    print(response.json())
                    print(response.json().get("access_token"))
                    return f'Authorization successful! You can close this window. Token: {access_token}'
                else:
                    logger.error('Access token not found in the response.')
                    return 'Authorization failed! Access token not found.', 400
            except requests.exceptions.JSONDecodeError as e:
                logger.error(f'Error parsing JSON response: {e}')
                return 'Authorization failed! Error parsing response.', 400
        else:
            print(response.text)
            logger.error(f'Request to token URL failed with status code {response.status_code}')
            return f'Authorization failed! Token request failed with status code {response.status_code}.', 400

    return 'Authorization failed! Missing code or state.', 400


# Register blueprint with Flask app
app.register_blueprint(oauth_blueprint)


def run_flask():
    app.run(host='0.0.0.0', port=80)


def main() -> None:
    global application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(
        MessageHandler(filters.TEXT & filters.Regex("^(Add secret key|Get list of my secret keys|Обратно в главную)$"),
                       handle_action_settings))
    application.add_handler(
        MessageHandler(filters.TEXT & filters.Regex(
            "^(Get my advertises|Get Advertise Statistics|Get User Information|Обратно в главную)$"),
                       handle_action_advertises))
    application.add_handler(
        MessageHandler(filters.TEXT & filters.Regex("^(OLX API|Secret Key Settings)$"), handle_action_main))
    application.add_handler(
        MessageHandler(filters.TEXT & filters.Regex("^(Advertises|My balance|Обратно в главную)$"),
                       handle_action_olx_api))
    # application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, input_data))
    application.add_handler(CommandHandler("start", start_button))
    application.add_handler(CallbackQueryHandler(save_secret_key))
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & filters.Regex("^(Create Advertise)$"),
                                     start)],
        states={
            FIRST: [MessageHandler(filters.TEXT & ~filters.COMMAND, first_argument)],
            SECOND: [MessageHandler(filters.TEXT & ~filters.COMMAND, second_argument)],
            THIRD: [MessageHandler(filters.TEXT & ~filters.COMMAND, third_argument)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    callback_query_handler = CallbackQueryHandler(get_advert_statistics, pattern='^select_advertise:')

    # Add this handler to your dispatcher
    application.add_handler(callback_query_handler)
    application.add_handler(conv_handler)
    # Start Flask app in a separate thread
    flask_thread = Thread(target=run_flask)
    flask_thread.start()

    # Start the Bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

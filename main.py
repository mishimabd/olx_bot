import logging

from telegram import Update
from telegram.ext import (Application,
                          CommandHandler,
                          MessageHandler,
                          filters,
                          CallbackQueryHandler,
                          CallbackContext)
from handlers import (input_data,
                      handle_action_settings,
                      handle_action_main,
                      save_secret_key,
                      handle_action_advertises,
                      handle_action_olx_api)
from buttons import start_button

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

CLIENT_ID = "your_client_id"
CLIENT_SECRET = "your_client_secret"
REDIRECT_URI = "http://myadomain.com/auth/connect"
TOKEN_URL = "https://www.olx.kz/api/open/oauth/token"
AUTH_URL = "https://www.olx.kz/oauth/authorize/"
TELEGRAM_BOT_TOKEN = "7051155336:AAEGyPRtiNELXFL5t2i2DNI5lRhLRJeSQMo"


def main() -> None:
    application = Application.builder().token("7051155336:AAEGyPRtiNELXFL5t2i2DNI5lRhLRJeSQMo").build()
    application.add_handler(
        MessageHandler(filters.TEXT & filters.Regex("^(Add secret key|Get list of my secret keys|Обратно в главную)$"),
                       handle_action_settings))
    application.add_handler(
        MessageHandler(filters.TEXT & filters.Regex("^(Get my advertises|"
                                                    "Promote my advertises|"
                                                    "Update my advertise|"
                                                    "Get advert statistics|"
                                                    "Обратно в главную)$"),
                       handle_action_advertises))
    application.add_handler(
        MessageHandler(filters.TEXT & filters.Regex("^(OLX API|"
                                                    "Secret Key Settings)$"), handle_action_main))
    application.add_handler(
        MessageHandler(filters.TEXT & filters.Regex("^(Advertises|"
                                                    "My balance|"
                                                    "Обратно в главную)$"), handle_action_olx_api))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, input_data))
    application.add_handler(CommandHandler("start", start_button))
    application.add_handler(CallbackQueryHandler(save_secret_key))
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

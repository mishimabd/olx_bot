import asyncio
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ConversationHandler, filters
import requests
import redis
from urllib.parse import urlparse, parse_qs
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep
from service_advertise import (
    get_statistic,
    first_argument,
    second_argument,
    third_argument,
    cancel,
    start,
    fourth_argument,
    fifth_argument,
    billing_history,
    packets_left,
    check_advertises,
    sixth_argument,
    schedule_publication,
    create_advertises_by_excel,
    handle_excel_file
)
from service_paid_features import get_paid_features
from handlers import (
    handle_action_settings,
    handle_action_main,
    handle_action_advertises,
    handle_action_olx_api
)
from buttons import start_button
from utils import refresh_token

FIRST, SECOND, THIRD, FOURTH, FIFTH, SIXTH, DATETIME = range(7)
FILE = range(1)

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

# Log the bot token for verification
logger.info(f"Using Telegram Bot Token: {TELEGRAM_BOT_TOKEN}")

# Initialize Redis client
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)


# Function to get OAuth code using Selenium
def get_oauth_code(username, password):
    driver = webdriver.Chrome()

    page_for_auth = f"{AUTH_URL}?client_id={CLIENT_ID}&response_type=code&state=x93ld3v&scope=read+write+v2"
    driver.get(page_for_auth)
    sleep(1)

    uname = driver.find_element(By.NAME, "username")
    uname.send_keys(username)
    p = driver.find_element(By.NAME, "password")
    p.send_keys(password)
    p.send_keys(Keys.RETURN)
    try:
        sleep(10)
        dang_this_cookie = driver.find_element(By.XPATH, '//*[@id="cookiesBar"]/a')
        dang_this_cookie.click()
        sleep(1)
        app = driver.find_element(By.NAME, "approve")
        app.click()
        logger.info("First method")
    except:
        logger.info("Second method")

    code = ""
    sleep(2)
    while True:
        get_url = driver.current_url
        sleep(1)
        if "/?code" in get_url:
            parsed_url = urlparse(get_url)
            code = parse_qs(parsed_url.query).get('code', [None])[0]
            break
    logger.info(f"Code: {code}")
    driver.quit()
    return code


def main():
    # Initialize the Telegram bot application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Set up handlers
    application.add_handler(
        MessageHandler(filters.TEXT & filters.Regex("^(Add secret key|Get list of my secret keys|Обратно в главную)$"),
                       handle_action_settings))
    application.add_handler(MessageHandler(
        filters.TEXT & filters.Regex("^(Все объявления|Статистика|Информация про пользователя|Обратно в главную)$"),
        handle_action_advertises))
    application.add_handler(
        MessageHandler(filters.TEXT & filters.Regex("^(OLX API|Информация про пользователя)$"), handle_action_main))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex("^(Объявления|Мой баланс|Обратно в главную)$"),
                                           handle_action_olx_api))
    application.add_handler(CommandHandler("start", start_button))

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & filters.Regex("^(Создать объявление)$"), start)],
        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, first_argument)],
            2: [MessageHandler(filters.TEXT & ~filters.COMMAND, second_argument)],
            3: [MessageHandler(filters.TEXT & ~filters.COMMAND, third_argument)],
            4: [MessageHandler(filters.TEXT & ~filters.COMMAND, fourth_argument)],
            5: [MessageHandler(filters.TEXT & ~filters.COMMAND, fifth_argument)],
            6: [MessageHandler(filters.PHOTO, sixth_argument)],
            7: [MessageHandler(filters.TEXT & ~filters.COMMAND, schedule_publication)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    application.add_handler(CommandHandler("get_paid_features", get_paid_features))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex("^(История затрат)$"), billing_history))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex("^(Остаток пакетов)$"), packets_left))

    conv_handler_excel = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & filters.Regex("^(Создать объявления по файлу)$"),
                                     create_advertises_by_excel)],
        states={
            1: [MessageHandler(
                filters.Document.MimeType("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
                handle_excel_file)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    application.add_handler(conv_handler_excel)
    application.add_handler(CallbackQueryHandler(get_statistic))

    # Set up background scheduler for token refresh
    scheduler = BackgroundScheduler()
    scheduler.add_job(refresh_token, 'interval', hours=3)
    scheduler.start()

    # Get OAuth code using Selenium
    username = "7761782677"
    password = "200320052010meir"
    code = get_oauth_code(username, password)

    if code:
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
        }
        response = requests.post(TOKEN_URL, data=data)
        logger.info(response.json())
        if response.status_code == 200:
            token_response = response.json()
            access_token = token_response.get('access_token')
            if access_token:
                redis_client.set('access_token', access_token)
                # Use a valid chat ID where you want to send the message
                chat_id = "1924374737"
                application.bot.send_message(chat_id=chat_id,
                                                   text=f'Authorization successful! Access token: {access_token}')
            else:
                logger.error('Access token not found in the response.')
        else:
            logger.error(f'Request to token URL failed with status code {response.status_code}')

    try:
        # Start the bot
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    finally:
        # Clean up resources
        scheduler.shutdown()
        application.shutdown()


if __name__ == "__main__":
    main()

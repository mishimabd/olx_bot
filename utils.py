import requests
from urllib.parse import urlparse, parse_qs

client_id = "200166"
CLIENT_ID = "200166"
CLIENT_SECRET = "Km1wN26hPhRaMhHkCGtLW8EjvPkLMn6Kwr10EhzrPci5NWot"
TOKEN_URL = "https://www.olx.kz/api/open/oauth/token"
AUTH_URL = "https://www.olx.kz/oauth/authorize/"
TELEGRAM_BOT_TOKEN = "7051155336:AAEGyPRtiNELXFL5t2i2DNI5lRhLRJeSQMo"


def get_token_client():
    url = "https://www.olx.kz/api/open/oauth/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "PostmanRuntime/7.39.0",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive"
    }
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": "Km1wN26hPhRaMhHkCGtLW8EjvPkLMn6Kwr10EhzrPci5NWot",
        "scope": "v2 read write"
    }
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print(f"Error: Failed to obtain access token. Status code: {response.status_code}, Content: {response.content}")
        return None


def get_token_auth(auth_code):
    url = "https://www.olx.kz/api/open/oauth/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive"
    }
    data = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": auth_code,
        "scope": "v2 read write",
        "redirect_uri": "https://185.4.180.8"
    }
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print(f"Error: Failed to obtain access token. Status code: {response.status_code}, Content: {response.content}")
        return None


def get_code_for_auth():
    url = (f"https://www.olx.kz/oauth/authorize/"
           f"?client_id={client_id}"
           f"&response_type=code"
           f"&scope=read+write+v2"
           f"&state=some_state_value")
    print(f"Please visit the following URL to authorize the application: {url}")
    return input("Enter the authorization code from the URL: ")

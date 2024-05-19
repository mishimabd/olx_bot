import requests
from urllib.parse import urlparse, parse_qs

client_id = "200166"


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


def get_token_auth():
    url = "https://www.olx.kz/api/open/oauth/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive"
    }
    data = {
        "grant_type": "authorization_code",
        "client_id": "200166",
        "client_secret": "Km1wN26hPhRaMhHkCGtLW8EjvPkLMn6Kwr10EhzrPci5NWot",
        "scope": "v2 read write",
        "code": get_code_for_auth()
    }
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        return None


def get_code_for_auth():
    url = (f"https://www.olx.kz/oauth/authorize/"
           f"?client_id={client_id}"
           f"&response_type=code"
           f"&scope=read+write+v2"
           f"&redirect_uri=https://t.me/@olx_advertise_bot")
    session = requests.Session()
    response = session.get(url, allow_redirects=True)
    final_url = response.url
    parsed_url = urlparse(final_url)
    query_params = parse_qs(parsed_url.query)
    token = query_params.get('code', [None])[0]

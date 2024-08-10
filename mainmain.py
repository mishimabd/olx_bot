import selenium
from time import sleep
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from urllib.parse import urlparse, parse_qs

# service = Service(executable_path="chromedriver_win32\chromedriver.exe")
driver = webdriver.Chrome()

username_test = "7761782677"
password_test = "200320052010meir"
init_page = "https://olx.kz"
page_for_auth = "https://www.olx.kz/oauth/authorize/?client_id=200166&response_type=code&state=x93ld3v&scope=read+write+v2"

driver.get(page_for_auth)
print(driver.title)
sleep(1)

uname = driver.find_element(By.NAME, "username")
uname.send_keys(username_test)
p = driver.find_element(By.NAME, "password")
p.send_keys(password_test)
p.send_keys(Keys.RETURN)
try:
    sleep(10)
    # approve   //*[@id="cookiesBar"]/a
    dang_this_cookie = driver.find_element(By.XPATH, '//*[@id="cookiesBar"]/a')
    dang_this_cookie.click()
    sleep(1)
    app = driver.find_element(By.NAME, "approve")
    app.click()
    print("First method")
except:
    print("Second method")

# Getting current URL
sleep(2)
while True:
    get_url = driver.current_url
    print(get_url)
    sleep(1)
    if "/?code" in get_url:
        parsed_url = urlparse(get_url)
        code = parse_qs(parsed_url.query).get('code', [None])[0]
        break
print(f"Code: {code}")

import asyncio

from selenium import webdriver
from selenium.webdriver.common.by import By
from asyncselenium.webdriver.remote.async_webdriver import AsyncWebdriver
from asyncselenium.webdriver.support.async_wait import AsyncWebDriverWait
from asyncselenium.webdriver.support import async_expected_conditions as ec
#from selenium.webdriver.firefox.options import Options
from selenium.webdriver.chrome.options import Options
import os
async def prepare_chrome_driver(user_id):
    chrome_options = webdriver.ChromeOptions()
    #Most Minimized version
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--headless')  
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-infobars')
    chrome_options.add_argument('--disable-notifications')

    profile_directory = f'profiles/{user_id}'
    if not os.path.exists(profile_directory):
        os.makedirs(profile_directory)
    chrome_options.add_argument(f"user-data-dir={profile_directory}")
    chrome_options.binary_location = 'chrome-linux64/chrome'
    driver = await AsyncWebdriver(options=chrome_options)
    return driver

# def prepare_firefox_driver(user_id):
#     options = Options()

#     profile_directory = f'profiles/{user_id}'
 
#     if not os.path.exists(profile_directory):
#         os.makedirs(profile_directory)
#         profile = webdriver.FirefoxProfile()
#         driver = webdriver.Firefox(firefox_profile=profile)

#     else:
#         options.profile = profile_directory
        
#         driver = webdriver.Firefox(options=options)
#     return driver

from selenium import webdriver
import asyncio
#from selenium.webdriver.firefox.options import Options
from selenium.webdriver.chrome.options import Options
import os
async def prepare_chrome_driver(user_id):
    chrome_options = Options()
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
    loop = asyncio.get_event_loop()
    driver = await loop.run_in_executor(None, lambda: webdriver.Chrome(options=chrome_options))
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

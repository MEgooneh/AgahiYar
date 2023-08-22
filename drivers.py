from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import os
def prepare_chrome_driver():
    #TODO:
    pass

def prepare_firefox_driver(user_id):
    options = Options()
    #options.add_argument('--headless')
    profile_directory = f'profiles/{user_id}'
    if not os.path.exists(profile_directory):
        os.makedirs(profile_directory)
    options.profile = profile_directory
    
    driver = webdriver.Firefox(options=options)
    return driver

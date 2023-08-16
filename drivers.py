from selenium import webdriver
from selenium.webdriver.firefox.options import Options
def prepare_chrome_driver():
    #TODO:
    pass

def prepare_firefox_driver():
    options = Options()
    #options.headless = True
    driver = webdriver.Firefox(options=options)
    return driver

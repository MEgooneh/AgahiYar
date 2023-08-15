from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
def prepare_chrome_driver():
    #TODO:
    pass

def prepare_firefox_driver():
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options)
    driver.get("google.com")
    print(driver.page_source)
    return driver

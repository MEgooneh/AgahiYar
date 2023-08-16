import formatting
from services.pkgs import *
import time
def login_attemp(driver , phone_number):
    driver.get('https://divar.ir/new')
    time.sleep(3)
    formatted_phone_number = formatting.phone_format(phone_number)
    driver.find_element(By.NAME, 'mobile').send_keys(formatted_phone_number)


def login_complete(driver , code):
    driver.find_element(By.NAME, 'code').send_keys(code)

    

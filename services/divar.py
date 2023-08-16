import formatting
from services.pkgs import *
import time, re
def login_attemp(driver , phone_number):
    driver.get('https://divar.ir/new')
    time.sleep(3)
    formatted_phone_number = formatting.phone_format(phone_number)
    driver.find_element(By.NAME, 'mobile').send_keys(formatted_phone_number)


def login_complete(driver , code):
    driver.find_element(By.NAME, 'code').send_keys(code)

def new_message_checker(driver):
    driver.get('https://divar.ir/chat')
    time.sleep(1)
    title = driver.title
    search_digits = re.search(r'\d+', title)
    new_messages_cnt = int(search_digits.group()) if search_digits else 0
    new_chats = [driver.find_element(By.CSS_SELECTOR,f'[data-indexincache="{i}"]').find_element(By.TAG_NAME,'a').get_attribute('href') for i in range(1,int(new_messages_cnt)+1)]
    return new_chats
    

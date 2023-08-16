import re
import responser
import time 
from services.pkgs import *
def new_message_checker(driver):
    driver.get('https://divar.ir/chat')
    time.sleep(1)
    title = driver.title
    search_digits = re.search(r'\d+', title)
    new_messages_cnt = search_digits if search_digits else 0
    new_chats = [driver.find_element(By.CSS_SELECTOR,f'[data-indexincache="{i}"]').find_element(By.TAG_NAME,'a').get_attribute('href') for i in range(1,int(new_messages_cnt)+1)]
    return new_chats
def answer_all(driver): 
    new_messages = new_message_checker(driver)
    #for i in range(new_messages):
    return 
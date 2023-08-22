import formatting
from selenium.webdriver.common.by import By
import time, re, logger
def login_attemp(driver , phone_number):
    driver.get('https://divar.ir/new')
    time.sleep(10)
    mobile_field = driver.find_element(By.NAME, 'mobile')
    if mobile_field: 
        mobile_field.send_keys(phone_number)
        logger.log("INFO", "divar", f"Successful login attemp... waiting for code, Phone:{phone_number}")
        return True
    else:
        logger.log("ERROR", "divar", f"Unsuccessful login attemp. Phone:{phone_number}")
        return False

    return

def login_complete(driver , code):
    code_field = driver.find_element(By.NAME, 'code')
    if code_field:
        code_field.send_keys(code)
        logger.log("INFO", "divar", "Login Completed!")
        return True
    else:
        logger.log("ERROR", "divar", f"Error in Code sumbition for logging in, Code:{code}")
        return False
    
def new_messages(driver):
    driver.get('https://divar.ir/chat')
    time.sleep(1)
    title = driver.title
    search_digits = re.search(r'\d+', title)
    new_messages_cnt = int(search_digits.group()) if search_digits else 0
    new_chats = [driver.find_element(By.CSS_SELECTOR,f'[data-indexincache="{i}"]').find_element(By.TAG_NAME,'a').get_attribute('href') for i in range(1,int(new_messages_cnt)+1)]
    return new_chats
    

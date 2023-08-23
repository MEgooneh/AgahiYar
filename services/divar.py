import formatting
from selenium.webdriver.common.by import By
import re, logger, asyncio
async def login_attemp(driver , phone_number):
    driver.get('https://divar.ir/new')
    mobile_field = driver.find_element(By.NAME, 'mobile')
    if mobile_field: 
        mobile_field.send_keys(phone_number)
        return True
    else:
        logger.log("ERROR", "divar", f"Unsuccessful login attemp. Phone:{phone_number}")
        return False

    return

async def login_complete(driver , code):
    code_field = driver.find_element(By.NAME, 'code')
    if code_field:
        code_field.send_keys(code)
        return True
    else:
        logger.log("ERROR", "services.divar", f"Error in Code sumbition for logging in, Code:{code}")
        return False
    
async def new_messages(driver):
    driver.get('https://divar.ir/chat')
    await asyncio.sleep(3)
    title = driver.title
    search_digits = re.search(r'\d+', title)
    new_messages_cnt = int(search_digits.group()) if search_digits else 0
    new_chats = [driver.find_element(By.CSS_SELECTOR,f'[data-indexincache="{i}"]').find_element(By.TAG_NAME,'a').get_attribute('href') for i in range(1,int(new_messages_cnt)+1)]
    return new_chats
    

import formatting
from asyncselenium.webdriver.remote.async_webdriver import AsyncWebdriver
from asyncselenium.webdriver.support.async_wait import AsyncWebDriverWait
from asyncselenium.webdriver.support import async_expected_conditions as ec
from selenium.webdriver.common.by import By
import re, logger, time, asyncio
async def login_attemp(driver , phone_number):
    await driver.get('https://divar.ir/new')
    wait = AsyncWebDriverWait(driver, 10)
    mobile_field = await wait.until(ec.presence_of_element_located((By.NAME, 'mobile'))) 
    if mobile_field: 
        await mobile_field.send_keys(phone_number)
        return True
    else:
        logger.log("ERROR", "divar", f"Unsuccessful login attemp. Phone:{phone_number}")
        return False

    return

async def login_complete(driver , code):
    wait = AsyncWebDriverWait(driver, 10)
    code_field = await wait.until(ec.presence_of_element_located((By.NAME, 'code')))
    if code_field:
        code_field.send_keys(code)
        return True
    else:
        logger.log("ERROR", "services.divar", f"Error in Code sumbition for logging in, Code:{code}")
        return False
    
async def new_messages(driver):
    await driver.get('https://divar.ir/chat')
    asyncio.sleep(3)
    title = driver.title
    search_digits = re.search(r'\d+', title)
    new_messages_cnt = int(search_digits.group()) if search_digits else 0
    wait = AsyncWebDriverWait(driver, 10)
    new_chats = [await wait.until(ec.presence_of_element_located(By.CSS_SELECTOR,f'[data-indexincache="{i}"]')).find_element(By.TAG_NAME,'a').get_attribute('href') for i in range(1,int(new_messages_cnt)+1)]
    return new_chats
    

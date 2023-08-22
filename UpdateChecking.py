import re
import responser
import time 
from services import divar
import drivers
import database_handle as db
def new_messages(driver , service):
    if service == "divar" : 
        return divar.new_messages(driver)
     

def answer(driver , chat_url):
    driver.get(chat_url)
    


    driver.back()

def answer_all(driver): 
    new_chats = new_messages(driver , "divar")
    for chat in new_chats :
        answer(driver , chat)    
    return 

def login(driver, user):
    divar.login_attemp(driver, user.phone)
    code = input("Enter the code:")
    divar.login_complete(driver, code)
    return

while(True):
    for user in db.get_active_users():
        driver = drivers.prepare_firefox_driver(user.chat_id)
        if user.logged_in == False : 
            login(driver , user)
            #TODO:
            if LOGIN_IS_SUCCESFUL:
                db.user_logged_in(user.chat_id)
        #answer_all(driver)
        driver.get("https://divar.ir/chat")
        time.sleep(30)
        driver.close()
    time.sleep(60)
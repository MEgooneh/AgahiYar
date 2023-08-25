import re
from playwright.sync_api import sync_playwright, Page, expect

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

def login(user):

    return context



with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=False)

    for user in db.get_active_users():
        if user.logged_in == False:
            continue 
        context = browser.new_context(storage_state=f".auth/{user.chat_id}.json")
        context.set_default_timeout(120000)
        page = context.new_page()
        page.goto('https://divar.ir/chat')
        print(page.title)




        context.close()


    


    

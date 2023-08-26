import re
from playwright.sync_api import sync_playwright, Page, expect

import database_handle as db


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


    


    

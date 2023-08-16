import re
import responser
import time 
import services
from services.pkgs import *
def new_message_checker(driver , service):
    if service == "divar" : 
        return services.divar.new_message_checker(driver)
     

def answer(driver , chat_url):
    driver.get(chat_url)
    


    driver.back()

def answer_all(driver): 
    new_chats = new_message_checker(driver)
    for chat in new_chats : 
        answer(driver , chat)    
    return 
import os
import database_handle as db
from services import divar
import logger, drivers, formatting
TOKEN = os.getenv("TG_KEY")



from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import  Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext


def start(update: Update, context: CallbackContext) -> int:
    chat_id = int(update.message.chat_id)
    user = db.get_user(chat_id)
    if user:
        update.message.reply_text(f"""
Welcome back!
{"You are logged in!" if user.logged_in else "You didn't logged in yet!"} 
                                  """)    
    else:
        update.message.reply_text(f"""
Welcome new user!
you can login with /login .
                                  """)





PHONE, CODE = range(2)


def login(update: Update, context: CallbackContext) -> int:
    chat_id = int(update.message.chat_id)
    if db.get_user(chat_id) == None:
        update.message.reply_text("Hi! Please provide your phone number.")    
    else:
        update.message.reply_text("You've already validated your code.")
        return ConversationHandler.END
    
    return PHONE

temp_driver = None

def receive_phone_number(update: Update, context: CallbackContext) -> int:
    chat_id = int(update.message.chat_id)
    phone = formatting.phone_format(update.message.text)
    update.message.reply_text("Please Wait... we are trying to login to divar.")
    db.add_user(chat_id, phone)
    global temp_driver
    temp_driver = drivers.prepare_firefox_driver(chat_id)
    print("DONE!")
    attemp = divar.login_attemp(temp_driver, phone)
    if attemp:
        update.message.edit_text("Done! Please enter the code you received.")
        return CODE
    else:
        update.message.edit_text("an Error occured, please try again later!")
        return ConversationHandler.END

def receive_code(update: Update, context: CallbackContext) -> int:
    chat_id = int(update.message.chat_id)
    completed_login = divar.login_complete(temp_driver, update.message.text)
    if completed_login :  # Replace with your validation logic
        update.message.reply_text("Code validated! You're all set.")
    else:
        update.message.reply_text("Invalid code. Please try again.")
    temp_driver.close()
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Conversation cancelled.", reply_markup=ReplyKeyboardRemove())
    if temp_driver:
        temp_driver.close()
    return ConversationHandler.END


if __name__ == '__main__':
    PROXY_URL = "https://210.230.238.153:443"
    PROXY_USERNAME = "your_proxy_username"
    PROXY_PASSWORD = "your_proxy_password"
    request_kwargs = {
        'proxy_url': PROXY_URL,
        # 'urllib3_proxy_kwargs': {
        #     'username': PROXY_USERNAME,
        #     'password': PROXY_PASSWORD,
        # }
    }
    #,  request_kwargs=request_kwargs
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    
    dispatcher.add_handler(CommandHandler('start' , start))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('login', login)],
        states={
            PHONE: [MessageHandler(Filters.text, receive_phone_number)],
            CODE: [MessageHandler(Filters.text, receive_code)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    dispatcher.add_handler(conv_handler)
    
    updater.start_polling()
    updater.idle()



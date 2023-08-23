import os
import database_handle as db
from services import divar
import drivers, formatting, logger, shutil, time

#TODO : for efficiency transfer one-used packages in just that function 

TOKEN = os.getenv("TG_KEY")

######## states:

PHONE, CODE, LINK, SURE, DESCRIPTION, LINK_DELETE, CHARGE_SBT = range(7)


from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram.ext import  Updater,filters, CommandHandler, MessageHandler, ConversationHandler, ApplicationBuilder, ContextTypes

reply_markup_cancel = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton("/cancel")],
        ],
        resize_keyboard=True
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = int(update.message.chat_id)
    user = db.get_user(chat_id)
    if user:
        await update.message.reply_text(f"""
Welcome back!
{"You are logged in!" if user.logged_in else "You didn't logged in yet!"} 
                                  """)    
    else:
        db.add_user(chat_id)
        await update.message.reply_text(f"""
Welcome new user!
you can login with /login .
                                  """)


async def helpp(update: Update, context:ContextTypes.DEFAULT_TYPE):
    help_message = """


"""
    await update.message.reply_text(help_message)    
    return

################## Add post

async def addPost(update: Update, context:ContextTypes.DEFAULT_TYPE):
    chat_id = int(update.message.chat_id)
    user = db.get_user(chat_id)
    if user.logged_in == False:
        await update.message.reply_text("You must login first!")
        return ConversationHandler.END
    remained = user.posts_charged - user.posts_number
    if remained == 0 : 
        await update.message.reply_text("You can't add any post. you have riched your limitation!")
    else:
        await update.message.reply_text(f"""
Ok!you have {remained} remaind posts, 
Please share your post url at divar. example : https://divar.ir/v/D23FCeda34?rel=android)
""", reply_markup = reply_markup_cancel)
    return LINK


async def recieve_posturl(update: Update, context:ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if formatting.is_url(url) == False:
        await update.message.reply_text("Please send a valid url.", reply_markup = reply_markup_cancel)
        return LINK
    global post
    post = db.Post()
    post.chat_id, post.url, post.post_id = int(update.message.chat_id), url, formatting.url_to_postid(url)
    await update.message.reply_text("Done! now tell the desciption and the tutorial for the ai to respond!", reply_markup = reply_markup_cancel)
    return DESCRIPTION

async def recieve_description(update: Update, context:ContextTypes.DEFAULT_TYPE):
    post.description = update.message.text
    db.add_post(post)
    await update.message.reply_text("Done! now you will be announced if someone ask you a Q in divar chat!")
    return ConversationHandler.END

async def cancel_post(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Conversation cancelled.")
    return ConversationHandler.END


################## Delete post

async def deletePost(update: Update, context:ContextTypes.DEFAULT_TYPE):
    user = db.get_user(int(update.message.chat_id))
    if user.logged_in == False:
        await update.message.reply_text("You must login first!")
        return ConversationHandler.END    
    await update.message.reply_text("Send the post url.")
    return LINK_DELETE


async def recieve_posturl_delete(update: Update, context:ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if formatting.is_url(url) == False:
        await update.message.reply_text("Please send a valid url.", reply_markup = reply_markup_cancel)
        return LINK_DELETE
    user = db.get_user(int(update.message.chat_id))
    post_id = formatting.url_to_postid(url)
    post = db.get_post(post_id)
    if post :
        db.delete_post(post) 
        await update.message.reply_text(f"Done! now you now have {user.posts_charged-user.posts_number + 1} chargs to post.")
    else:
        await update.message.reply_text("you have no such post!")

    return ConversationHandler.END

################## Login



async def login(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = int(update.message.chat_id)
    if db.get_user(chat_id).logged_in == False:
        await update.message.reply_text("Hi! Please provide your phone number.", reply_markup = reply_markup_cancel)   
        return PHONE

    else:
        await update.message.reply_text("You've already validated your code.")
        return ConversationHandler.END
    

temp_driver = None

async def receive_phone_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = int(update.message.chat_id)
    phone = formatting.phone_format(update.message.text)
    await update.message.reply_text("Please Wait... we are trying to login to divar.", reply_markup = reply_markup_cancel)
    user = db.get_user(chat_id)
    user.phone = phone
    logger.log("INFO", "db", f"{chat_id} set the phone number to {phone}.") 
    db.update()
    global temp_driver
    temp_driver = await drivers.prepare_chrome_driver(chat_id)
    attemp = await divar.login_attemp(temp_driver, phone)
    if attemp:
        await time.sleep(5)
        await update.message.reply_text("Done! Please enter the code you received.", reply_markup = reply_markup_cancel)
        return CODE
    else:
        await update.message.reply_text("an Error occured, please try again later with /login!")
        return ConversationHandler.END

async def receive_code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = int(update.message.chat_id)
    completed_login = await divar.login_complete(temp_driver, update.message.text)
    if completed_login :  # Replace with your validation logic
        await update.message.reply_text("Code validated! You're all set.")
        await time.sleep(5)
        db.user_logged_in(chat_id)
        temp_driver.close()
        return ConversationHandler.END
    else:
        await update.message.reply_text("Invalid code. Please try again later.")
        return ConversationHandler.END

async def cancel_login(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Conversation cancelled.")
    if temp_driver:
        db.user_logged_out(int(update.message.chat_id))
        temp_driver.close()
    return ConversationHandler.END


################## logout

async def logout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int : 
    user = db.get_user(int(update.message.chat_id))
    if user.logged_in == False:
        await update.message.reply_text("you are already loggedout.")
        return ConversationHandler.END    
    await update.message.reply_text("Are you sure? type your phone number if you want to logout.")
    return SURE

async def logout_sure(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int : 
    phone = formatting.phone_format(update.message.text)
    user = db.get_user(int(update.message.chat_id))
    if user.phone != phone :
        await update.message.reply_text("this is not the phone that you have logged in !")
        return ConversationHandler.END
    db.user_logged_out(int(update.message.chat_id))
    await shutil.rmtree(f'profiles/{user.chat_id}')
    await update.message.reply_text("you are logged out. and your folder deleted!")
    return ConversationHandler.END

########################## charge

async def chargeStart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int : 
    user = db.get_user(int(update.message.chat_id))    
    await update.message.reply_text("please send the serial number you have:")
    return CHARGE_SBT

async def recieve_serial(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int : 
    serial = update.message.text
    user = db.get_user(int(update.message.chat_id))
    verified_serial = db.get_serial(serial)
    if verified_serial == None or verified_serial.remained == 0 :
        await update.message.reply_text("Wrong serial or you can't use it anymore!")
        return ConversationHandler.END

    if str(user.chat_id) in verified_serial.users : 
        await update.message.reply_text("You have uses this code before!")
        return ConversationHandler.END

    user.posts_charge += verified_serial.charge
    verified_serial.remained -= 1
    verified_serial.users += ('-' + str(user.chat_id))
    db.update()
    await update.message.reply_text(f"Your charge increased {verified_serial.charge}. now you have {user.posts_charge} !")
    return ConversationHandler.END


if __name__ == '__main__':
    
    #updater = Updater(token=TOKEN, use_context=True)
    application = ApplicationBuilder().token(TOKEN).build()
    #dispatcher = updater.application
    
    application.add_handler(CommandHandler('start' , start))
    application.add_handler(CommandHandler('help' , helpp))


    login_handler = ConversationHandler(
        entry_points=[CommandHandler('login', login)],
        states={
            PHONE: [MessageHandler(filters.TEXT, receive_phone_number)],
            CODE: [MessageHandler(filters.TEXT, receive_code)]
        },
        fallbacks=[CommandHandler('cancel', cancel_login)]
    )

    post_handler = ConversationHandler(
        entry_points=[CommandHandler('addpost', addPost)],
        states={
            LINK: [MessageHandler(filters.TEXT, recieve_posturl)],
            DESCRIPTION: [MessageHandler(filters.TEXT, recieve_description)]
        },
        fallbacks=[CommandHandler('cancel', cancel_post)]
    )

    logout_handler = ConversationHandler(
        entry_points=[CommandHandler('logout', logout)],
        states={
            SURE: [MessageHandler(filters.TEXT, logout_sure)],
        },
        fallbacks=[CommandHandler('cancel', cancel_post)]
    )    

    deletepost_handler = ConversationHandler(
        entry_points=[CommandHandler('deletepost', deletePost)],
        states={
            LINK_DELETE: [MessageHandler(filters.TEXT, recieve_posturl_delete)],
        },
        fallbacks=[CommandHandler('cancel', cancel_post)]
    )    
    charge_handler = ConversationHandler(
        entry_points=[CommandHandler('charge', chargeStart)],
        states={
            CHARGE_SBT: [MessageHandler(filters.TEXT, recieve_serial)],
        },
        fallbacks=[CommandHandler('cancel', cancel_post)]
    )       


    
    application.add_handler(login_handler)
    application.add_handler(post_handler)
    application.add_handler(deletepost_handler)
    application.add_handler(charge_handler)
    application.add_handler(logout_handler)

    application.run_polling()
    # updater.start_polling()
    # updater.idle()



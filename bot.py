import os, asyncio, openaiapi
import database_handle as db
from playwright.async_api import async_playwright, expect
import formatting, logger, json

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

########## /start

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

############## /help

async def helpp(update: Update, context:ContextTypes.DEFAULT_TYPE):
    help_message = """


"""
    await update.message.reply_text(help_message)    
    return

################## /addpost

async def detail_post(post):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        context.set_default_timeout(120000)
        page = await context.new_page()
        await page.goto(post.url)
        await asyncio.sleep(3)
        await page.screenshot(path=f'images/{post.chat_id}/{post.post_id}.png',full_page=True)
        # post.category
        values_locator = page.locator('.kt-breadcrumbs__link')
        values = await values_locator.evaluate_all("list => list.map(element => element.textContent)")
        post.category = '/'.join(values[:-1])

        # post.fields
        title_locator = page.locator('.kt-base-row__title')
        value_locator = page.locator('.kt-unexpandable-row__value')
        titles = await title_locator.evaluate_all("list => list.map(element => element.textContent)")
        values = await value_locator.evaluate_all("list => list.map(element => element.textContent)")
        data = dict(zip(titles, values))
        json_data = json.dumps(data, ensure_ascii=False)
        post.fields = json_data

        # post.description
        element_locator = page.locator('.kt-description-row__text--primary')
        element_text = await element_locator.text_content()
        post.description = element_text

        # post.title 
        locator = page.locator('.kt-page-title__subtitle')
        title = await locator.text_content()
        post.title = title

        db.update()



async def gen_Q(post):
    prompt = f""" you are a buyer and there is a classified ad with this details :

title : {post.title}
description : {post.description}
details : {post.fields}
category: {post.category}

################    
ask 5 short questions from seller about this ad that is unclear in the details of the post.
you must ask questions in persian.
in your response you must just send questions seperated by '/' : 
"""
    questions = await openaiapi.send_message(prompt)
    return questions

async def addPost(update: Update, context:ContextTypes.DEFAULT_TYPE):
    chat_id = int(update.message.chat_id)
    user = db.get_user(chat_id)
    if user.logged_in == False:
        await update.message.reply_text("You must login first!")
        return ConversationHandler.END
    remained = user.posts_charged - user.posts_number
    if remained == 0 : 
        await update.message.reply_text("You can't add any post. you have riched your limitation!")
        return ConversationHandler.END
    else:
        await update.message.reply_text(f"""
Ok!you have {remained} remaind posts, 
Please share your post url at divar. example : https://divar.ir/v/D23FCeda34?rel=android)
""")
    return LINK


async def recieve_posturl(update: Update, context:ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if formatting.is_url(url) == False:
        await update.message.reply_text("Please send a valid url.")
        return LINK
    await update.message.reply_text("Ok now wait for a minute to extract the details of the post.")
    post = db.Post()
    post.chat_id, post.url, post.post_id = int(update.message.chat_id), url, formatting.url_to_postid(url)
    await detail_post(post) 
    with open(f'images/{update.message.chat_id}/{post.post_id}.png', 'rb') as photo_file : 
        await context.bot.send_photo(chat_id=update.message.chat_id,photo=photo_file,caption="This is your post")

    questions = await gen_Q(post)
    context.user_data['questions'] = questions
    context.user_data['post'] = post

    await update.message.reply_text(f"now answer this questions about your post with / seperated : \n{questions}")
    return DESCRIPTION

async def recieve_description(update: Update, context:ContextTypes.DEFAULT_TYPE):
    answers = update.message.text.split('/')
    QA = [(context.user_data['questions'].split('/')[i] , answers[i]) for i in range(len(answers))]
    post = context.user_data['post']
    post.questions = json.dumps(QA, ensure_ascii=False)
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
        await update.message.reply_text("Please send a valid url.")
        return LINK_DELETE
    user = db.get_user(int(update.message.chat_id))
    post_id = formatting.url_to_postid(url)
    post = db.get_post(post_id)
    if post:
        db.delete_post(post) 
        os.remove(f'images/{post.chat_id}/{post.post_id}.png')
        await update.message.reply_text(f"Done! now you now have {user.posts_charged-user.posts_number + 1} chargs to post.")
    else:
        await update.message.reply_text("you have no such post!")

    return ConversationHandler.END

################## Login

user_data = {}

async def login_submit(chat_id , code , phone):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        context.set_default_timeout(120000)
        page = context.new_page()
        page = await context.new_page()
        await page.goto("https://divar.ir/new")
        await page.get_by_placeholder("شمارهٔ موبایل").fill(phone)
        await asyncio.sleep(10)
        await page.get_by_placeholder("کد تأیید ۶ رقمی").fill(code)
        await asyncio.sleep(10)
        storage = await context.storage_state(path=f".auth/{chat_id}.json")
        context.close()
        browser.close()
     
    return True
    


async def login_attemp(chat_id, phone):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        context.set_default_timeout(120000)
        page = await context.new_page()
        await page.goto("https://divar.ir/new" )
        await page.get_by_placeholder("شمارهٔ موبایل").fill(phone)
        await asyncio.sleep(10)

async def login(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = int(update.message.chat_id)
    if db.get_user(chat_id).logged_in == False:
        await update.message.reply_text("Hi! Please provide your phone number.")   
        return PHONE

    else:
        await update.message.reply_text("You've already validated your code.")
        return ConversationHandler.END
    
attemp = None 

async def receive_phone_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = int(update.message.chat_id)
    phone = formatting.phone_format(update.message.text)
    context.user_data['phone'] = phone
    await update.message.reply_text("Please Wait... we are trying to login to divar.")
    user = db.get_user(chat_id)
    user.phone = phone
    logger.log("INFO", "db", f"{chat_id} set the phone number to {phone}.") 
    db.update()
    await login_attemp(chat_id , phone)
    await update.message.reply_text("Enter the code:")
    return CODE


async def receive_code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = int(update.message.chat_id)
    await login_submit(chat_id , update.message.text, context.user_data['phone'])
    await update.message.reply_text("Code validated! You're all set.")
    db.user_logged_in(chat_id)
    return ConversationHandler.END

async def cancel_login(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Conversation cancelled.")
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
    await os.remove(f'.auth/{user.chat_id}.json')
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
        await update.message.reply_text("You have used this code before!")
        return ConversationHandler.END

    user.posts_charged += verified_serial.charge
    verified_serial.remained -= 1
    verified_serial.users += ('-' + str(user.chat_id))
    db.update()
    await update.message.reply_text(f"Your charge increased {verified_serial.charge}. now you have {user.posts_charged} !")
    return ConversationHandler.END


if __name__ == '__main__':
    
    application = ApplicationBuilder().token(TOKEN).build()
    
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



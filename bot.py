import os, asyncio, openaiapi
import database_handle as db
from playwright.async_api import async_playwright, expect
import formatting, logger, json

TOKEN = os.getenv("TG_KEY")
headless_condition = True
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

########## unrecognized command 
async def handle_unrecognized(update, context):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="دستور شناسایی نشد!")




########## /start

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = int(update.message.chat_id)

    user = db.get_user(chat_id)
    if user:
        await update.message.reply_text(f"""
👋 سلامی دوباره.
{"شما در حال حاضر با {user.phone} وارد شده‌اید!" if user.logged_in else "شما هنوز اکانتی متصل به دیوار ندارید! برای اینکار از دستور /login استفاده کنید."} 
""")    
    else:
        db.add_user(chat_id)
        await update.message.reply_text(f"""
👋 خوش آمدید!
برای اتصال اکانتتان به دیوار از /login استفاده کنید.
همچنین برای دیدن راهنما از /help کمک بگیرید.
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
        browser = await p.chromium.launch(headless=headless_condition)
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
        await update.message.reply_text("""🔴 شما هنوز ورود نکرده‌اید!
برای اینکار دستور /login را وارد کنید.""")
        return ConversationHandler.END
    remained = user.posts_charged - user.posts_number
    if remained == 0 : 
        await update.message.reply_text("""🔴 اعتبار شما به پایان رسیده است!
برای افزایش اعتبار کدسریال را از @adconnect_admin خریداری کنید. در صورتی که کدسریال دارید با دستور /charge آن را فعال کنید.""")
        return ConversationHandler.END
    else:
        await update.message.reply_text(f"""
🟢 شما {remained} آگهی می‌توانید ثبت کنید.

⚪️ اکنون لینک آگهی مدنظرتان را از قسمت share دیوار کپی کنید و در اینجا وارد کنید:

(بطور مثال : https://divar.ir/v/D23FCeda34?rel=android )
""")
    return LINK


async def recieve_posturl(update: Update, context:ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if formatting.is_url(url) == False:
        await update.message.reply_text("🔴 لینک نامعتبر است. دوباره تلاش کنید.")
        return LINK
    await update.message.reply_text("🟠 لحظاتی منتظر بمانید تا اطلاعات آگهی استخراج شود...")
    post = db.Post()
    post.chat_id, post.url, post.post_id = int(update.message.chat_id), url, formatting.url_to_postid(url)
    await detail_post(post) 
    with open(f'images/{update.message.chat_id}/{post.post_id}.png', 'rb') as photo_file : 
        await context.bot.send_photo(chat_id=update.message.chat_id,photo=photo_file,caption="📊 این نمای آگهی شماست که دریافت کردیم.")

    questions = await gen_Q(post)
    context.user_data['questions'] = questions
    context.user_data['post'] = post

    await update.message.reply_text(f"""⚪️ به سوالات زیر در مورد آگهی خود جواب دهید.

⚠️ توجه داشته باشید که جواب های شما باید با '/' از هم جدا شوند. بطور مثال : قیمت مقطوع است / بله کاملا سالم است / ...

❓سوالات : 
                                    
{questions}""")
    return DESCRIPTION

async def recieve_description(update: Update, context:ContextTypes.DEFAULT_TYPE):
    answers = update.message.text.split('/')
    QA = [(context.user_data['questions'].split('/')[i] , answers[i]) for i in range(len(answers))]
    post = context.user_data['post']
    post.questions = json.dumps(QA, ensure_ascii=False)
    db.add_post(post)
    await update.message.reply_text("""🟢 انجام شد!

اکنون این آگهی توسط سرورها خوانده می‌شود و به مشتریان پاسخ داده خواهد شد!""")
    return ConversationHandler.END

async def cancel_post(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("این گفتگو لغو شد!")
    return ConversationHandler.END


################## Delete post

async def deletePost(update: Update, context:ContextTypes.DEFAULT_TYPE):
    user = db.get_user(int(update.message.chat_id))
    if user.logged_in == False:
        await update.message.reply_text("""🔴 شما هنوز ورود نکرده‌اید!

برای اینکار دستور /login را وارد کنید.""")
        return ConversationHandler.END    
    await update.message.reply_text("""⚪️ اکنون لینک آگهی مدنظرتان را از قسمت share دیوار کپی کنید و در اینجا وارد کنید:

(بطور مثال : https://divar.ir/v/D23FCeda34?rel=android )""")
    return LINK_DELETE


async def recieve_posturl_delete(update: Update, context:ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if formatting.is_url(url) == False:
        await update.message.reply_text("🔴 لینک نامعتبر است. دوباره تلاش کنید.")
        return LINK_DELETE
    user = db.get_user(int(update.message.chat_id))
    post_id = formatting.url_to_postid(url)
    post = db.get_post(post_id)
    if post:
        db.delete_post(post) 
        os.remove(f'images/{post.chat_id}/{post.post_id}.png')
        await update.message.reply_text(f"🟢 شما اکنون می‌توانید {user.posts_charged-user.posts_number} آگهی ثبت کنید.")
    else:
        await update.message.reply_text("you have no such post!")

    return ConversationHandler.END

################## Login

user_data = {}

async def login_submit(chat_id , code , phone):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless_condition)
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
        browser = await p.chromium.launch(headless=headless_condition)
        context = await browser.new_context()
        context.set_default_timeout(120000)
        page = await context.new_page()
        await page.goto("https://divar.ir/new" )
        await page.get_by_placeholder("شمارهٔ موبایل").fill(phone)
        await asyncio.sleep(10)

async def login(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = int(update.message.chat_id)
    if db.get_user(chat_id).logged_in == False:
        await update.message.reply_text("لطفا شماره تلفنی که با آن در دیوار آگهی منتشر کرده‌اید را وارد کنید:")   
        return PHONE

    else:
        await update.message.reply_text("🟠 شما قبلا به اکانت دیوار متصل شدید. درصورتی که میخواهید شماره ی جدیدی وارد شوید ابتدا با دستور /logout خارج شوید و سپس از همین دستور برای ورود مجدد استفاده کنید.")
        return ConversationHandler.END
    
attemp = None 

async def receive_phone_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = int(update.message.chat_id)
    phone = formatting.phone_format(update.message.text)
    context.user_data['phone'] = phone
    await update.message.reply_text("🟠 لحظاتی منتظر بمانید تا ما به اکانت شما وارد شویم...")
    user = db.get_user(chat_id)
    user.phone = phone
    logger.log("INFO", "db", f"{chat_id} set the phone number to {phone}.") 
    db.update()
    await login_attemp(chat_id , phone)
    await update.message.reply_text("کدی که به شماره‌ی شما پیامک شده را وارد کنید:")
    return CODE


async def receive_code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = int(update.message.chat_id)
    code = formatting.english_number(update.message.text)
    await login_submit(chat_id , code, context.user_data['phone'])
    await update.message.reply_text("🟢 کد شما تایید شد. اکنون می‌توانید با /addpost آگهی اضافه کنید.")
    db.user_logged_in(chat_id)
    return ConversationHandler.END

async def cancel_login(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("این گفتگو لغو شد!")
    return ConversationHandler.END


################## logout

async def logout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int : 
    user = db.get_user(int(update.message.chat_id))
    if user.logged_in == False:
        await update.message.reply_text("🔴 شما هنوز ورود نکرده‌اید!")
        return ConversationHandler.END    
    await update.message.reply_text("""⚠️ مطمعنید که می‌خواهید از این اکانت خارج شوید؟
برای اینکار لطفا شماره تماسی که با آن وارد شدید را مجددا وارد کنید:""")
    return SURE

async def logout_sure(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int : 
    phone = formatting.phone_format(update.message.text)
    user = db.get_user(int(update.message.chat_id))
    if user.phone != phone :
        await update.message.reply_text("🔴 این شماره‌ای نیست که با آن وارد شده‌اید!")
        return ConversationHandler.END
    db.user_logged_out(int(update.message.chat_id))
    await os.remove(f'.auth/{user.chat_id}.json')
    await update.message.reply_text("⚪️ شما با موفقیت خارج شدید! اطلاعات ورود شما هم از سرور پاک شد.")
    return ConversationHandler.END

########################## charge

async def chargeStart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int : 
    user = db.get_user(int(update.message.chat_id))   
    remained = user.posts_charged - user.posts_number 
    await update.message.reply_text(f"""⚪️ شما هم‌اکنون {remained} اعتبار دارید!

لطفا کد سریال خود را برای افزایش اعتبار وارد کنید:
(در صورتی که کدسریال ندارید باید از @adconnect_admin تهیه کنید!)""")
    return CHARGE_SBT

async def recieve_serial(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int : 
    serial = update.message.text
    user = db.get_user(int(update.message.chat_id))
    verified_serial = db.get_serial(serial)
    if verified_serial == None or verified_serial.remained == 0 :
        await update.message.reply_text("🔴 کد سریال نامعتبر است!")
        return ConversationHandler.END

    if str(user.chat_id) in verified_serial.users : 
        await update.message.reply_text("🟠 شما قبلا از این کد استفاده کرده‌اید!")
        return ConversationHandler.END

    user.posts_charged += verified_serial.charge
    verified_serial.remained -= 1
    verified_serial.users += ('-' + str(user.chat_id))
    db.update()
    await update.message.reply_text(f"""🎁 اعتبار شما افزایش یافت!

{verified_serial.charge} به اعتبار شما اضافه شد!

شما اکنون {user.posts_charged} اعتبار دارید!""")
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
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_unrecognized))

    application.run_polling()



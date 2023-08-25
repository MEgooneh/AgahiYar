import asyncio
from playwright.async_api import async_playwright, Page, expect

p = async_playwright()
browser = p.chromium.launch()

async def login_submit(page : Page , context,  code, chat_id):
    page.get_by_placeholder("کد تأیید ۶ رقمی").fill(code)
    storage = await context.storage_state(path=f".auth/{chat_id}.json")
    context.close()
    
async def login_attemp(chat_id, phone):
    context = await browser.new_context()
    page = await context.new_page()
    await page.goto("https://divar.ir/new")
    page.get_by_placeholder("شمارهٔ موبایل").fill(phone)
    return (page, context)







# # Save storage state into the file.
# storage = await context.storage_state(path="state.json")

# # Create a new context with the saved storage state.
# context = await browser.new_context(storage_state="state.json")

######
from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://divar.ir/")
    page.get_by_role("link", name="ثبت آگهی").click()
    page.get_by_placeholder("شمارهٔ موبایل").click()
    page.get_by_placeholder("شمارهٔ موبایل").fill("9354375897")
    page.get_by_placeholder("کد تأیید ۶ رقمی").fill("874081")
    page.get_by_role("button", name=" دیوار من").click()
    page.get_by_role("link", name=" آگهی‌های من").click()
    page.get_by_role("link", name="سیر تا پیاز عربی دوازدهم نهایی سیر تا پیاز عربی دوازدهم نهایی ۱۲۰,۰۰۰ تومان هفتهٔ پیش در جنت‌آباد جنوبی وضعیت آگهی: منتشر شده مدیریت آگهی").click()
    page.get_by_role("link", name="divar.ir/v/AZZ30Oud").click()
    page.get_by_text("کاملا کاملا نو و ارزان").click()
    page.get_by_text("سیر تا پیاز عربی دوازدهم نهایی۱ هفته پیش در تهران، جنت‌آباد جنوبیاطلاعات تماس چت").click()
    page.locator("div").filter(has_text=re.compile(r"^سیر تا پیاز عربی دوازدهم نهایی$")).click()
    page.get_by_role("button", name="اطلاعات تماس", exact=True).click()
    page.get_by_role("button", name=" چت").click()
    page.goto("https://divar.ir/chat")
    page.locator(".sb20e1").click()
    page.locator(".sb20e1").click()
    page.locator(".sb20e1").click()
    page.locator(".sb20e1").click()
    page.get_by_placeholder("متنی بنویسید").fill("ssghl ildkal odgd ;li ;hlgh k,ui ")
    page.get_by_placeholder("متنی بنویسید").press("Enter")
    page.get_by_placeholder("متنی بنویسید").fill("سلام همینشم خیلی کمه واقعا نوعه چون")
    page.get_by_placeholder("متنی بنویسید").press("Enter")
    page.get_by_role("link", name="کاربر دیوار منم پیدا نمیکنم. میخواید تو تلگرام آیدی @MEgooneh لوکیشنتون رو ارسال کنید فرمول بیست گاج ، فرمول ۲۰ ، امتحان نهایی دوازدهم فرمول بیست گاج ، فرمول ۲۰ ، امتحان نهایی دوازدهم  ۵/۲۴ آگهی من").click()

    # ---------------------
    context.close()
    browser.close()


# with sync_playwright() as playwright:
#     run(playwright)





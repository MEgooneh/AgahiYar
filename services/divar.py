from phone_number_formatter import phone_format

def login_attemp(driver , phone_number):
    driver.get('https://divar.ir/new')
    formatted_phone_number = phone_format(phone_number)
    driver.find_element(By.NAME, 'mobile').send_keys(formatted_phone_number)


def login_complete(driver , code):
    driver.find_element(By.NAME, 'code').send_keys(code)

    

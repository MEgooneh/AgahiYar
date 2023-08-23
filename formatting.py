import re
def phone_format(phone):
    persian_to_english = {
        '۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4',
        '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9'
    }
    for char in persian_to_english : 
        phone.replace(char , persian_to_english[char])
    if len(phone) == 11: 
        return phone[1:]
    if phone[0] == '+' : 
        return phone[3:]
    if phone[:2] == '98':
        return phone[2:]
    return phone

def is_url(url):
    url_regex = re.compile(r'^https?://(?:www\.)?[\w\-]+(\.[\w\-]+)+\S*$')
    return bool(url_regex.match(url))

def url_to_postid(url):
    return url.split('/')[-1].split('?')[0]

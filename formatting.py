def phone_format(phone):
    if len(phone) == 11 : 
        return phone[1:]
    if phone[0] == '+' : 
        return phone[3:]
    if phone[:2] == '98':
        return phone[2:]
    return phone

def url_to_postid(url):
    return url.split('/')[-1]

import random, string
import database_handle as db

def serial_gen():
    cases = string.ascii_lowercase + string.ascii_uppercase + string.digits
    return ''.join([random.choice(cases) for i in range(10)])





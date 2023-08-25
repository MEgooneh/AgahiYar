import random, string
import database_handle as db

def serial_gen():
    cases = string.ascii_lowercase + string.ascii_uppercase + string.digits
    return ''.join([random.choice(cases) for i in range(10)])

def submit_camp_serials():
    db.add_serial("testistest", 2 , 20)


if __name__ == "__main__" : 
    submit_camp_serials()


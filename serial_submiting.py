import random, string
import database_handle as db

def serial_gen():
    cases = string.ascii_lowercase + string.ascii_uppercase + string.digits
    return ''.join([random.choice(cases) for i in range(10)])

def submit_camp_serials():
    db.add_serial("testistest", 2 , 30)


if __name__ == "__main__" : 
    db.add_serial("genx" , 1 , 20)
    # for i in range(40) :
    #     code = serial_gen()
    #     db.add_serial(code, 1 , 1)
    #     print(code)
    # for i in range(30):
    #     code = serial_gen()
    #     print(code)
    #     db.add_serial(code , 5 , 1)
    # for i in range(20):   
    #     code = serial_gen()
    #     print(code) 
    #     db.add_serial(code , 10 , 1)
    # submit_camp_serials()
    # db.add_serial("mofid43", 2 , 30)


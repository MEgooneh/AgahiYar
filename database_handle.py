from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base

import formatting, logger

DATABASE_URL = 'sqlite:///adconnect.db'  # Replace with your database URL
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)


Base = declarative_base()

# Define the User model
class User(Base):
    __tablename__ = 'users'
    chat_id = Column(Integer, primary_key=True) # Needed
    phone = Column(String)
    posts_number = Column(Integer)
    posts_charged = Column(Integer)
    logged_in = Column(Boolean)
class Post(Base):
    __tablename__ = 'posts'
    post_id = Column(String, primary_key=True) # Needed
    url = Column(String, primary_key=True)
    title= Column(String)
    price = Column(String)
    auto = Column(Boolean)
    ai_note = Column(String)
    category = Column(String)
    questions = Column(String)
    chat_id = Column(Integer) # Needed
    description = Column(String)

class SerialNumber(Base):
    __tablename__ = 'serials'
    serial_id = Column(String , primary_key=True)
    charge = Column(Integer)
    remained = Column(Integer)
    users = Column(String)
# # Create the tables
Base.metadata.create_all(engine)

session = Session()


def update():
    session.commit()
    


def get_serial(s_id):
    
    serial = session.query(SerialNumber).filter_by(serial_id = s_id).first()
    return serial 

def add_serial(serial_id, charge , remained):
    
    serial = SerialNumber(serial_id=serial_id, charge=charge, remained=remained, users="")
    session.add(serial)
    logger.log("INFO", "db", f"{serial_id} serial added to database with charge:{charge} and remained:{remained}.")
    session.commit()
    
######################Users


def add_user(chat_id):
    
    user = User(chat_id = chat_id, posts_number=0, posts_charged=0, logged_in=False)
    session.add(user)
    logger.log("INFO", "db", f"{user.chat_id} added to database.")
    session.commit()
    
        


def user_logged_in(user_id):
    
    user = session.query(User).filter_by(chat_id=user_id).first()
    if user:
        user.logged_in = True
        logger.log("INFO", "db", f"{user_id} logged_in = TRUE")
    else:
        logger.log("WARNING", "db", f"{user_id} is not added, but tried to login!")

    session.commit()
    
        

def user_logged_out(user_id):
    
    user = session.query(User).filter_by(chat_id=user_id).first()
    if user:
        user.logged_in = False
        logger.log("INFO", "db", f"{user_id} logged_in = FALSE")
    else:
        logger.log("WARNING", "db", f"{user_id} is not added, but tried to logout!")
    session.commit()
    
    

def get_active_users(): 
    
    active_users = session.query(User).filter(User.posts_number > 0).all()
    
    return active_users

def get_user(chat_id):
    
    user=session.query(User).filter_by(chat_id=chat_id).first()
    
    return user

def delete_all_users():
    for i in session.query(User).all():
        session.delete(i)
#################Posts

def add_post(post):
    
    user = session.query(User).filter_by(chat_id=post.chat_id).first()
    if user:
        user.posts_number += 1
        session.add(post)
        logger.log("INFO", "db", f"{post.chat_id} added a post {post.post_id} to database.")
    session.commit()
    
    

def delete_post(post):
    
    session.delete(post)
    user = get_user(post.chat_id)
    user.posts_number -= 1
    logger.log("INFO", "db", f"{post.chat_id} deleted {post.post_id} from database.")
    session.commit()
    
    



def get_post(post_id):
    

    post = session.query(Post).filter_by(post_id=post_id).first()
    
    
    return post

def get_user_posts(chat_id):
    
    posts = session.query(Post).filter_by(chat_id=chat_id).all()
    
    return posts
        
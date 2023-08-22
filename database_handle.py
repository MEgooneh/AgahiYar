from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.mysql import insert


import formatting

# Define the database connection
DATABASE_URL = 'sqlite:///adconnect.db'  # Replace with your database URL
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# Define the base class for declarative models
Base = declarative_base()

# Define the User model
class User(Base):
    __tablename__ = 'users'
    chat_id = Column(Integer, primary_key=True)
    phone = Column(String)
    posts_number = Column(Integer)
    logged_in = Column(Boolean)
class Post(Base):
    __tablename__ = 'posts'
    post_id = Column(String, primary_key=True)
    title= Column(String)
    chat_id = Column(Integer)
    active = Column(Boolean)
    price_1 = Column(Integer)
    price_2 = Column(Integer)
    description = Column(Integer)


# # Create the tables
Base.metadata.create_all(engine)


######################Users


def add_user(user_id, *args):
    session=Session()
    new_user = User(chat_id = user_id, posts_number=0, logged_in=False)
    if len(args) > 0 : 
        new_user.phone = args[0]
    session.add(new_user)
    session.commit()
    session.close()


def update_user_phone(user_id , phone):
    session=Session()

    user = session.query(User).filter_by(chat_id = user_id).first()
    if user:
        user.phone = phone
    session.commit()
    session.close()


def user_logged_in(user_id):
    session=Session()

    user = session.query(User).filter_by(chat_id=user_id).first()
    if user:
        user.logged_in = True
    session.commit()
    session.close()


def get_active_users(): 
    session=Session()

    active_users = session.query(User).filter(User.posts_number > 0).all()
    session.close()
    
    return active_users

def get_user(chat_id):
    session=Session()

    user=session.query(User).filter_by(chat_id=chat_id).first()
    session.close()
    return user

#################Posts

def add_post(post_id, title, chat_id, price1 , price2 , description):
    session=Session()

    new_post = Post(post_id=post_id, title=title, chat_id=chat_id, price_1=price1, price_2=price2, description=description)
    user = session.query(User).filter_by(chat_id=chat_id).first()
    if user:
        user.posts_number += 1
    session.add(new_post)
    session.commit()
    session.close()


def deactive_post(post_id):
    session=Session()

    post = session.query(Post).filter_by(post_id=post_id).first()
    if post:
        post.active = False
    user = session.query(User).filter_by(chat_id=post.chat_id).first()
    if user:
        user.posts_number -= 1
    session.commit()
    session.close()


def get_post(post_id):
    session=Session()

    post = session.query(Post).filter_by(post_id=post_id).first()
    session.close()
    
    return post
def get_user_posts(chat_id):
    session=Session()

    posts = session.query(Post).filter_by(chat_id=chat_id).all()
    session.close()
    return posts
    

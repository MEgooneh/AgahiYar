import asyncio
from sqlalchemy import  Column, Integer, String, Boolean
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base

import formatting, logger

DATABASE_URL = 'sqlite+aiosqlite:///adconnect.db'   # Replace with your database URL
async_engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = sessionmaker(async_engine)

# Use async_session to create an asynchronous session factory

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
    chat_id = Column(Integer) # Needed
    description = Column(String)



async def update():
    async with AsyncSessionLocal() as session:
        await session.commit()
        

######################Users


async def add_user(chat_id):
    async with AsyncSessionLocal() as session:
        user = User(chat_id = chat_id, posts_number=0, posts_charged=3, logged_in=False)
        session.add(user)
        logger.log("INFO", "db", f"{user.chat_id} added to database.")
        await session.commit()
        


async def user_logged_in(user_id):
    async with AsyncSessionLocal() as session:
        user = session.query(User).filter_by(chat_id=user_id).first()
        if user:
            user.logged_in = True
            logger.log("INFO", "db", f"{user_id} logged_in = TRUE")
        else:
            logger.log("WARNING", "db", f"{user_id} is not added, but tried to login!")

        await session.commit()
        

async def user_logged_out(user_id):
    async with AsyncSessionLocal() as session:
        user = session.query(User).filter_by(chat_id=user_id).first()
        if user:
            user.logged_in = False
            logger.log("INFO", "db", f"{user_id} logged_in = FALSE")
        else:
            logger.log("WARNING", "db", f"{user_id} is not added, but tried to logout!")
        await session.commit()
    

async def get_active_users(): 
    async with AsyncSessionLocal() as session:
        active_users = session.query(User).filter(User.posts_number > 0).all()
        
        return active_users

async def get_user(chat_id):
    async with AsyncSessionLocal() as session:
        user=session.query(User).filter_by(chat_id=chat_id).first()
        
        return user

#################Posts

async def add_post(post):
    async with AsyncSessionLocal() as session:
        user = session.query(User).filter_by(chat_id=post.chat_id).first()
        if user:
            user.posts_number += 1
            session.add(post)
            logger.log("INFO", "db", f"{post.chat_id} added a post {post.post_id} to database.")
        await session.commit()
    

async def delete_post(post):
    async with AsyncSessionLocal() as session:
        session.delete(post)
        user = get_user(post.chat_id)
        user.posts_number -= 1
        logger.log("INFO", "db", f"{post.chat_id} deleted {post.post_id} from database.")
        await session.commit()
    



async def get_post(post_id):
    async with AsyncSessionLocal() as session:

        post = session.query(Post).filter_by(post_id=post_id).first()
        
        
        return post

async def get_user_posts(chat_id):
    async with AsyncSessionLocal() as session:

        posts = session.query(Post).filter_by(chat_id=chat_id).all()
        
        return posts
        

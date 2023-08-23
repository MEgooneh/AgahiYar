from sqlalchemy import  create_engine,Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base



DATABASE_URL = 'sqlite:///adconnect.db'  # Replace with your database URL
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)




Base = declarative_base()

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

# # Create the tables
Base.metadata.create_all(engine)
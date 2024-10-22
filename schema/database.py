from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from core.config import settings
Base = declarative_base()


class Messages(Base):
    __tablename__ = 'messages'

    message_id = Column(Integer, primary_key = True, autoincrement = True)
    user_id = Column(Text, nullable = False)
    message = Column(Text, nullable = False)
    creat_time = Column(DateTime, default=func.now())



class Users(Base):
    __tablename__ = 'users'

    user_id = Column(Text, nullable = False, primary_key = True)
    name = Column(Text)
    gender = Column(Text)
    age = Column(Integer, default = 60)
    nationality = Column(Text)
    address = Column(Text)
    acute_diseases = Column(Text)
    chronic_diseases = Column(Text)
    disability_status = Column(Text)
    mental_state = Column(Text)
    daily_routine = Column(Text)
    diet = Column(Text)
    exercise = Column(Text)
    hobby = Column(Text)
    income = Column(Text)
    consume_info = Column(Text)
    price_sensity = Column(Text)
    marital_status = Column(Text)
    children_situation = Column(Text)
    life_status = Column(Text)
    other = Column(Text)

def create_all():
    url = settings.mysql.db_url.replace("asyncmy", "pymysql")
    print(url)
    engine = create_engine(url, echo=True)
    Base.metadata.create_all(engine)
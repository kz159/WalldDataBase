"""
Reprsenets all walld models
"""
from sqlalchemy import (ARRAY, Binary, Boolean, Column, DateTime, Integer,
                        String, JSON, func)
from sqlalchemy.ext.declarative import declarative_base

BASE = declarative_base()

def get_psql_dsn(user, passw, host, port, db_name):
    return f'postgresql://{user}:{passw}@{host}:{port}/{db_name}'

class Permissions:
    Admin = 0
    Accept_pics = 1
    etc = 123


class User(BASE):
    """
    Represents User
    """
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    nickname = Column(String)
    telegram_id = Column(Integer)
    avail = Column(Boolean, default=True) # TODO УБРАТЬ НАХ ПОТОМ
    permissions = Column(ARRAY(Integer)) # Accept or decline
    pics_uploaded = Column(Integer, default=0)
    pics_accepted = Column(ARRAY(Integer)) #  id of pics
    register_date = Column(DateTime, server_default=func.now())
    telegram_last_message_id = Column(Integer)
    json_review = Column(JSON) # Хранить тут что ли всю инфу о пикче??


class Picture(BASE):
    """
    Represents picture from our db
    """
    __tablename__ = "pictures"
    pic_id = Column(Integer, primary_key=True)
    height = Column(Integer)
    width = Column(Integer)
    colour_hex = Column(Binary)
    category = Column(String)
    sub_category = Column(String)
    tags = Column(ARRAY(String))
    NSFW = Column(Boolean)
    source = Column(String)
    service = Column(String)

"""
Reprsenets all walld models
"""
from sqlalchemy import (ARRAY, Binary, Boolean, Column, DateTime, Integer,
                        String, func)
from sqlalchemy.ext.declarative import declarative_base
from config import DB_HOST, DB_PASSWORD, DB_PORT, DB_USER, DB_NAME

BASE = declarative_base()

DB_DSN = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'


class Permissions:
    Admin = 0
    Accept_pics = 1
    etc = 123


class User(BASE):
    """
    Represents User
    """
    __tablename__ = 'Users'
    user_id = Column(Integer, primary_key=True)
    nickname = Column(String)
    permissions = Column(ARRAY(Integer)) # Accept or decline
    pics_uploaded = Column(Integer, default=0)
    pics_accepted = Column(ARRAY(Integer)) #  id of pics
    register_date = Column(DateTime, server_default=func.now())


class Picture(BASE):
    """
    Represents picture from our db
    """
    __tablename__ = "Pictures"
    pic_id = Column(Integer)
    height = Column(Integer)
    width = Column(Integer)
    colour_hex = Column(Binary)
    category = Column(String)
    sub_category = Column(String)
    tags = Column(ARRAY(String))
    NSFW = Column(Boolean)
    source = Column(String)
    service = Column(String)

"""
Reprsenets all walld models
"""
from sqlalchemy import (ARRAY, Binary, Boolean, Column, DateTime, Integer,
                        String, JSON, func, ForeignKey)
from sqlalchemy.ext.declarative import declarative_base

BASE = declarative_base()

def get_psql_dsn(user, passw, host, port, db_name):
    return f'postgresql://{user}:{passw}@{host}:{port}/{db_name}'


class ModStates:
    available = 0
    got_picture = 1
    choosing_category = 2
    making_category = 3
    choosing_sub_directory = 4
    making_sub_directory = 5
    adding_tags = 6


class AdminStates:
    available = 0
    raising_user = 1


class User(BASE):
    """
    Represents User
    """
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    nickname = Column(String)
    telegram_id = Column(Integer)
    pics_uploaded = Column(Integer, default=0)
    register_date = Column(DateTime, server_default=func.now())


class Admin(BASE):
    """
    Represents Admin user
    with their states etc
    """
    __tablename__ = 'admins'
    admin_id = Column(Integer, ForeignKey('users.user_id'), primary_key=True)
    tg_state = Column(Integer, default=0)


class Moderator(BASE):
    """
    All users that have
    accept and decline pics
    will go here
    """
    __tablename__ = 'moderators'
    mod_id = Column(Integer, ForeignKey('users.user_id'), primary_key=True)
    pics_accepted = Column(ARRAY(Integer)) #  id of pics
    json_review = Column(JSON) # Хранить тут что ли всю инфу о пикче??
    tg_state = Column(Integer, default=0)
    last_message = Column(Integer)


class Category(BASE):
    """
    Represents list of categories
    """
    __tablename__ = "categories"
    category_id = Column(Integer, primary_key=True)
    category_name = Column(String, unique=True)

class SubCategory(BASE):
    """
    Represents list of subcategories for each category
    """
    __tablename__ = "sub_categories"
    sub_category_id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey('categories.category_id'))
    sub_category_name = Column(String, unique=True)


class Picture(BASE):
    """
    Represents picture from our db
    """
    __tablename__ = "pictures"
    pic_id = Column(Integer, primary_key=True)
    uploader_id = Column(Integer, ForeignKey('users.user_id'))
    height = Column(Integer)
    width = Column(Integer)
    colour_hex = Column(Binary)
    category = Column(Integer, ForeignKey('categories.category_id'))
    sub_category = Column(Integer, ForeignKey('sub_categories.sub_category_id'))
    tags = Column(ARRAY(String))
    source = Column(String)
    service = Column(String)

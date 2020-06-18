"""
Reprsenets all walld models
"""
from typing import Optional

from pydantic import BaseModel
from sqlalchemy import (JSON, Binary, Column, DateTime, ForeignKey,
                        Integer, String, Table, func, ARRAY)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import relationship

BASE = declarative_base()

def get_psql_dsn(user, passw, host, port, db_name):
    return f'postgresql://{user}:{passw}@{host}:{port}/{db_name}'


class ModStates:
    available = 0
    got_picture = 1
    choosing_category = 2
    making_category = 3
    choosing_sub_category = 4
    making_sub_category = 5
    choosing_tags = 6
    making_tags = 7
    done = 8

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
    telegram_id = Column(Integer, unique=True)
    pics_uploaded = Column(Integer, default=0)
    register_date = Column(DateTime, server_default=func.now())


class Admin(BASE):
    """
    Represents Admin user
    with their states etc
    """
    __tablename__ = 'admins'
    admin_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    tg_state = Column(Integer, default=0)


class Moderator(BASE):
    """
    All users that have
    accept and decline pics
    will go here
    """
    __tablename__ = 'moderators'
    mod_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    pics_accepted = Column(Integer, default=0) #  id of pics
    json_review = Column(MutableDict.as_mutable(JSON)) # Хранить тут что ли всю инфу о пикче??
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


class Tag(BASE):
    __tablename__ = "tags"
    tag_id = Column(Integer, primary_key=True)
    tag_name = Column(String)
    #tag_name = relationship("Picture", back_populates="tags")

assosiation = Table('assosiation',
                    BASE.metadata,
                    Column('tag_id', Integer, ForeignKey('tags.tag_id')),
                    Column('pic_id', Integer, ForeignKey('pictures.pic_id'))
)

class Picture(BASE):
    """
    Represents picture from our db
    """
    __tablename__ = "pictures"
    pic_id = Column(Integer, primary_key=True)
    uploader_id = Column(Integer, ForeignKey('users.user_id'))
    mod_review_id = Column(Integer, ForeignKey('moderators.mod_id'))
    service = Column(String)
    height = Column(Integer)
    width = Column(Integer)
    colours = Column(ARRAY(Binary))
    category = Column(Integer, ForeignKey('categories.category_id'))
    sub_category = Column(Integer, ForeignKey('sub_categories.sub_category_id'))
    tags = relationship('Tag', secondary=assosiation)
    source_url = Column(String)
    path = Column(String)
    url = Column(String)


class RejectedPicture(BASE): 
    """
    Represents rejected pictures by moderators
    """
    # TODO ПЕРЕИМЕНОВАТЬ В seenpictures что бы
    #  сразу иметь ввиду что мы это уже видели
    __tablename__ = 'rejected_pictures'
    id = Column(Integer, primary_key=True)
    mod_id = Column(Integer, ForeignKey('moderators.mod_id'))
    uploader = Column(String) # User or crawler
    url = Column(String, nullable=False)

class SeenPicture(BASE):
    """
    Represents url sources that
    was already seen by crawlers
    """
    __tablename__ = 'seen_pictures'
    id = Column(Integer, primary_key=True)
    url = Column(String, nullable=False, unique=True)

class PictureValid(BaseModel): # TODO ОТРАЗИТЬ ВСЕ ИЗМЕНЕНИЯ
    service: str
    height: int
    width: int
    source_url: str
    download_url: str
    preview_url: str

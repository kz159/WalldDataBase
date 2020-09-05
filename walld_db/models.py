"""
Reprsenets all walld models
"""

from pydantic import BaseModel, constr
from typing import List, Optional
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
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    telegram_id = Column(Integer, unique=True)
    pics_uploaded = Column(Integer, default=0)
    register_date = Column(DateTime, server_default=func.now())


class Admin(BASE):
    """
    Represents Admin user
    with their states etc
    """
    __tablename__ = 'admin'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    tg_state = Column(Integer, default=0)


class Moderator(BASE):
    """
    All users that have
    accept and decline pics
    will go here
    """
    __tablename__ = 'moderator'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    pics_accepted = Column(Integer, default=0)  # id of pics
    json_review = Column(MutableDict.as_mutable(JSON))  # Хранить тут что ли всю инфу о пикче??
    tg_state = Column(Integer, default=0)
    last_message = Column(Integer)


class Category(BASE):
    """
    Represents list of categories
    """
    __tablename__ = "category"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    sub_categories = relationship("SubCategory", lazy='joined')


class SubCategory(BASE):
    """
    Represents list of subcategories for each category
    """
    __tablename__ = "sub_category"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    category_id = Column(Integer, ForeignKey('category.id'))


class Tag(BASE):
    __tablename__ = "tag"
    id = Column(Integer, primary_key=True)
    name = Column(String)


associated = Table('associated',
                   BASE.metadata,
                   Column('tag_id', Integer, ForeignKey('tag.id')),
                   Column('pic_id', Integer, ForeignKey('picture.id')))


class Picture(BASE):
    """
    Represents picture from our db
    """
    __tablename__ = "picture"
    id = Column(Integer, primary_key=True)
    uploader_id = Column(Integer, ForeignKey('user.id'))
    mod_review_id = Column(Integer, ForeignKey('moderator.id'))
    service = Column(String)
    height = Column(Integer)
    width = Column(Integer)
    colours = Column(ARRAY(String))
    category = Column(Integer, ForeignKey('category.id'))
    sub_category = Column(Integer, ForeignKey('sub_category.id'))
    tags = relationship('Tag', secondary=associated)
    source_url = Column(String)
    path = Column(String)
    url = Column(String)


class RejectedPicture(BASE): 
    """
    Represents rejected pictures by moderators
    """
    __tablename__ = 'rejected_pictures'
    id = Column(Integer, primary_key=True)
    mod_id = Column(Integer, ForeignKey('moderator.id'))
    uploader = Column(String)  # User or crawler
    url = Column(String, nullable=False)


class SeenPicture(BASE):
    """
    Represents url sources that
    was already seen by crawlers
    """
    __tablename__ = 'seen_picture'
    id = Column(Integer, primary_key=True)
    url = Column(String, nullable=False, unique=True)


class PictureValid(BaseModel):  # TODO ОТРАЗИТЬ ВСЕ ИЗМЕНЕНИЯ И УБРАТЬ ЭТО В ГРАББЕРА
    service: str
    height: int
    width: int
    source_url: str
    download_url: str
    preview_url: str

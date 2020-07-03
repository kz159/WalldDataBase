'''
Module with usefull classes for all microservices
'''
from contextlib import contextmanager
import logging
from time import sleep

import pika
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, Query
from walld_db.models import (Category, Moderator, RejectedPicture, SeenPicture,
                             Tag, User, get_psql_dsn, Picture, SubCategory)

# TODO ATEXIT STUFF
LOG = logging.getLogger(__name__)


class DB:
    def __init__(self, user, passwd, host, port, name, echo=False):
        dsn = get_psql_dsn(user, passwd, host, port, name)
        LOG.info('connecting to db...')
        self.engine = self.get_engine(dsn, echo=echo)
        self.session_maker = sessionmaker(bind=self.engine)
        LOG.info('successfully connected to db!') # TODO неа, не нравки

    @staticmethod
    def get_engine(dsn, echo):
        return sa.create_engine(dsn, echo=echo)

    @contextmanager
    def get_connection(self):
        with self.engine.connect() as connection:
            yield connection

    @contextmanager
    def get_session(self, expire=False, commit=True):
        session = self.session_maker(expire_on_commit=expire)
        try:
            yield session
        except ValueError: # TODO Более качественную обработку ошибок бы
            session.rollback()
        finally:
            if commit:
                session.commit()
            session.close()

    @property
    def categories(self):
        with self.get_session(commit=False) as ses:
            cats = ses.query(Category.category_name).all()
            return [i[0] for i in cats]

    @property # Удаление?
    def rejected_pictures(self):
        with self.get_session(commit=False) as ses:
            pics = ses.query(RejectedPicture.url).all()
            pics = [i[0] for i in pics] or []
            return pics

    @property
    def picture_urls(self):
        with self.get_session(commit=False) as ses:
            pics = ses.query(Picture.url).all()
            pics = [i[0] for i in pics] or []
            return pics

    @property
    def picture_objects(self):
        with self.get_session(commit=False) as ses:
            pics = ses.query(Picture).all()
            return pics

    @property
    def categories_objects(self):
        with self.get_session(commit=False) as ses:
            return ses.query(Category).all()

    @property
    def seen_pictures(self):
        with self.get_session(commit=False) as ses:
            pics = ses.query(SeenPicture.url).all()
            pics = [i[0] for i in pics] or []
            return pics

# TODO GETTER SETTER FOR PICTURES
    def add_seen_pic(self, url):
        with self.get_session() as ses:
            ses.add(SeenPicture(url=url))

    @property
    def users(self) -> list:
        with self.get_session(commit=False) as ses:
            users = ses.query(User.nickname)
        return [i[0] for i in users]

    @property
    def tags(self) -> list:
        with self.get_session(commit=False) as ses:
            return ses.query(Tag).all()

    @property
    def named_tags(self) -> list:
        with self.get_session(commit=False) as ses:
            tags = ses.query(Tag.tag_name)
            return [i[0] for i in tags]

    def get_pics(self, **questions):

        cat = questions.get('category')
        sub_cat = questions.get('sub_category')
        tags = questions.get('tags')
        colours = questions.get('colours')

        with self.get_session(commit=False) as ses:
            pics = ses.query(Picture)
            if cat:
                cat = self.get_category(category_name=cat, session=ses)
                pics = pics.filter_by(category=getattr(cat, 'category_id', None))
            if sub_cat:
                sub_cat = self.get_sub_category(sub_category_name=sub_cat)
                pics = pics.filter_by(sub_category=sub_cat)

            # TODO colours, tags

        return pics.all()

    def get_tag(self, tag_id=None, tag_name=None, session=None):
        if not session: # TODO Хуйня, переделай
            with self.get_session(commit=False) as ses:
                if tag_name:
                    return ses.query(Tag).filter_by(tag_name=tag_name).one_or_none()
                if tag_id:
                    return ses.query(Tag).filter_by(tag_id=tag_id).one_or_none()
        if tag_name:
            return session.query(Tag).filter_by(tag_name=tag_name).one_or_none()
        if tag_id:
            return session.query(Tag).filter_by(tag_id=tag_id).one_or_none()

    def get_category(self, category_name=None, cat_id=None, session=None):
        if category_name:
            query = Query(Category).filter_by(category_name=category_name)
        elif cat_id:
            query = Query(Category).filter_by(category_id=cat_id)

        if session:
            cat = query.with_session(session)
        else:
            with self.get_session(commit=False) as ses:
                cat = query.with_session(ses)
        return cat.one_or_none()
# TODO squash that three functions!
    def get_sub_category(self, sub_category_name=None, sub_cat_id=None, session=None):
        if sub_category_name: # В разы лучше!
            query = Query(SubCategory).filter_by(sub_category_name=sub_category_name)
        elif sub_cat_id:
            query = Query(SubCategory).filter_by(sub_category_id=sub_cat_id)

        if session:
            cat = query.with_session(session)
        else:
            with self.get_session(commit=False) as ses:
                cat = query.with_session(ses)

        return cat.one()

    def get_state(self, tg_id, table): # TODO add sessions
        with self.get_session(commit=False) as ses:
            l = ses.query(User, table.tg_state).\
                join(table, User.user_id == table.user_id).\
                filter(User.telegram_id == tg_id)
            l = l.one_or_none()
            if l:
                return l[1]
            return l

    def get_moderator(self, tg_id, session=None):
        l = session.query(User, Moderator).\
            join(Moderator, User.user_id == Moderator.user_id).\
            filter(User.telegram_id==tg_id).one()
        return l


class Rmq:
    def __init__(self,
                 host='localhost',
                 port='5672',
                 user="guest",
                 passw='guest'):
        self.creds = pika.PlainCredentials(user, passw)
        self.params = pika.ConnectionParameters(host=host,
                                                port=port,
                                                credentials=self.creds,
                                                heartbeat=60)
        LOG.info('connecting to rmq....')
        while True:
            try:
                self.connection = pika.BlockingConnection(self.params)
                break
            except pika.exceptions.AMQPConnectionError:
                LOG.error('cant connect to rmq!')
                sleep(1)
                continue

        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='check_out', durable=True)
        self.channel.queue_declare(queue='go_sql', durable=True)
        LOG.info('successfully connected to rmq')

    def get_message(self, amount: int, queue_name: str):
        self.channel.basic_qos(prefetch_count=amount)
        method, props, body = next(self.channel.consume(queue_name))
        self.channel.cancel()
        self.channel.basic_ack(method.delivery_tag)
        return body

    @property
    def durable(self):
        return pika.BasicProperties(delivery_mode=2)

"""
Module with useful classes for all microservices
"""
from contextlib import contextmanager
import logging
from time import sleep
import sys
import pika
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, Query
from walld_db.models import (Category, Moderator, RejectedPicture, SeenPicture,
                             Tag, User, get_psql_dsn, Picture, SubCategory)
from walld_db.constants import DEFAULT_FORMATTER
from typing import List
from pathlib import Path

# TODO AT EXIT STUFF
LOG = logging.getLogger(__name__)


class DB:
    def __init__(self, user, passwd, host, port, name, echo=False):
        dsn = get_psql_dsn(user, passwd, host, port, name)
        LOG.info('connecting to db...')
        self.engine = self.get_engine(dsn, echo=echo)
        self.session_maker = sessionmaker(bind=self.engine)
        LOG.info('successfully connected to db!')  # TODO неа, не нравки

    @staticmethod
    def get_engine(dsn, echo):
        return sa.create_engine(dsn, echo=echo)

    @contextmanager
    def get_connection(self):
        with self.engine.connect() as connection:
            yield connection

    @contextmanager  # TODO remove this bc we have connection.begin()
    def get_session(self, expire=False, commit=True):
        session = self.session_maker(expire_on_commit=expire)
        try:
            yield session
        except ValueError:  # TODO Более качественную обработку ошибок бы
            session.rollback()
        finally:
            if commit:
                session.commit()
            session.close()

    @property
    def categories(self):
        with self.get_session(commit=False) as ses:
            cats = ses.query(Category.name).all()
            return [i[0] for i in cats]

    @property  # Удаление?
    def rejected_pictures(self):
        with self.get_session(commit=False) as ses:
            pics = ses.query(RejectedPicture.url).all()
            pics = [i[0] for i in pics] or []
            return

    @property
    def picture_urls(self):
        with self.get_session(commit=False) as ses:
            pics = ses.query(Picture.url).all()
            pics = [i[0] for i in pics] or []
            return pics

    # @property https://www.depesz.com/2007/09/16/my-thoughts-on-getting-random-row/
    # https://www.2ndquadrant.com/en/blog/tablesample-in-postgresql-9-5-2/
    # def random_pic(self):
    #     with self.get_session(commit=False) as ses:
    #         ses.

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
    def seen_pictures(self) -> List[str]:
        with self.get_session(commit=False) as ses:
            pics = ses.query(SeenPicture.url).all()
            pics = [i[0] for i in pics] or []
            return pics

    def add_seen_pic(self, url):
        with self.get_session() as ses:
            ses.add(SeenPicture(url=url))

    @property
    def users(self) -> List[str]:
        with self.get_session(commit=False) as ses:
            users = ses.query(User.name)
        return [i[0] for i in users]

    @property
    def tags(self) -> List[Tag]:
        with self.get_session(commit=False) as ses:
            return ses.query(Tag).all()

    @property
    def named_tags(self) -> List[str]:
        with self.get_session(commit=False) as ses:
            tags = ses.query(Tag.name)
            return [i[0] for i in tags]

    def get_pics(self, **questions) -> List[Picture]:
        cat = questions.get('category')
        sub_cat = questions.get('sub_category')
        tags = questions.get('tags')

        # TODO colours = questions.get('colours')

        with self.get_session(commit=False) as ses:
            pics = ses.query(Picture)

            if cat:
                cat = self.get_row(Category, name=cat, session=ses)
                pics = pics.filter_by(category=getattr(cat, 'id', None))

            if sub_cat:
                sub_cat = self.get_row(SubCategory, name=sub_cat, session=ses)
                pics = pics.filter_by(sub_category=getattr(sub_cat, 'id', None))

            if tags:
                pics = pics.filter(Picture.tags.in_(tags))  # TODO refactor after tags will be selectable

            LOG.debug(f'Got this query {str(pics)}')
            # TODO colours, tags

        return pics.all()

    def get_row(self, table, session=None, **kwargs):
        query = Query(table).filter_by(**kwargs)

        if session:
            result = query.with_session(session)

        else:
            with self.get_session(commit=False) as ses:
                result = query.with_session(ses)

        return result.one_or_none()

    def get_state(self, tg_id, table):  # TODO add sessions
        with self.get_session(commit=False) as ses:
            l = ses.query(User, table.tg_state). \
                join(table, User.id == table.user_id). \
                filter(User.telegram_id == tg_id)
            l = l.one_or_none()
            if l:
                return l[1]
            return l

    def get_moderator(self, tg_id, session=None):
        # if session:  # TODO
        l = session.query(User, Moderator). \
            join(Moderator, User.id == Moderator.user_id). \
            filter(User.telegram_id == tg_id).one()
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
        self.connect()
        self.channel.queue_declare(queue='check_out', durable=True)
        self.channel.queue_declare(queue='go_sql', durable=True)

        LOG.info('successfully connected to rmq')

    def get_message(self, amount: int, queue_name: str):
        while True:
            try:
                self.channel.basic_qos(prefetch_count=amount)
                method, props, body = next(self.channel.consume(queue_name))
                self.channel.cancel()
                self.channel.basic_ack(method.delivery_tag)
                break
            except pika.exceptions.StreamLostError:
                LOG.warning('server missed our heartbeats!, reconnecting...')
                self.connect()
                continue
        return body

    def connect(self):
        while True:
            try:
                LOG.info('connecting to rmq....')
                self.connection = pika.BlockingConnection(self.params)
                self.channel = self.connection.channel()
                break
            except pika.exceptions.AMQPConnectionError:
                LOG.error('cant connect to rmq!')
                sleep(1.5)
                continue

    @property
    def durable(self):
        return pika.BasicProperties(delivery_mode=2)


def logger_factory(name: str, level: str = 'INFO',
                   formatter: str = DEFAULT_FORMATTER,
                   log_to_file: Path = None, stream=sys.stdout):

    _log_formatter = logging.Formatter(formatter)
    log = logging.getLogger(name)

    _stdout_handler = logging.StreamHandler(stream)
    _stdout_handler.setFormatter(_log_formatter)

    if log_to_file:
        sys_file_handler = logging.FileHandler(log_to_file)
        sys_file_handler.setFormatter(_log_formatter)
        log.addHandler(sys_file_handler)

    log.addHandler(_stdout_handler)
    log.setLevel(level)
    return log

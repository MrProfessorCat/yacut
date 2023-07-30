from datetime import datetime
from http import HTTPStatus
import random
import re

from . import db
from .app_constants import (
    AVAILABLE_CHARS_FOR_SHORT_ID, MAX_SHORT_URL_LENGTH
)
from .error_handlers import InvalidAPIUsage


class URLMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String, nullable=False)
    short = db.Column(db.String)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    @staticmethod
    def get_unique_short_id(segment_length):
        return ''.join(
            random.choice(AVAILABLE_CHARS_FOR_SHORT_ID) for _ in range(segment_length)
        )

    @classmethod
    def from_dict(cls, data):
        for field in ['original', 'short']:
            if field in data:
                setattr(cls, field, data[field])

    @staticmethod
    def get(short_id):
        return URLMap.query.filter_by(short=short_id).first()

    @staticmethod
    def get_or_404(short_id):
        data = URLMap.query.filter_by(short=short_id).first()
        if not data:
            raise InvalidAPIUsage('Указанный id не найден', HTTPStatus.NOT_FOUND)
        return data

    @staticmethod
    def is_short_id_correct(short_id):
        return (
            len(short_id) <= MAX_SHORT_URL_LENGTH and
            bool(re.fullmatch(f'[{AVAILABLE_CHARS_FOR_SHORT_ID}]+', short_id))
        )

    @staticmethod
    def generate_short_id():
        short_id = URLMap.get_unique_short_id(MAX_SHORT_URL_LENGTH)
        if not URLMap.get(short_id):
            return short_id
        raise InvalidAPIUsage(
            'Закончились доступные адреса!',
            HTTPStatus.BAD_REQUEST
        )

    @staticmethod
    def save(original, short_id):
        if not short_id:
            short_id = URLMap.generate_short_id()
        print('short_id = ', short_id)
        if URLMap.get(short_id):
            raise InvalidAPIUsage(
                'Имя "{}" уже занято.'.format(short_id)
            )
        if URLMap.is_short_id_correct(short_id):
            link = URLMap(original=original, short=short_id)
            db.session.add(link)
            db.session.commit()
            return link
        else:
            raise InvalidAPIUsage(
                'Указано недопустимое имя для короткой ссылки',
                HTTPStatus.BAD_REQUEST
            )

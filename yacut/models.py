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
    def __get_unique_short_id(segment_length):
        return ''.join(
            random.choices(AVAILABLE_CHARS_FOR_SHORT_ID, k=segment_length)
        )

    def from_dict(self, data):
        for field in ['original', 'short']:
            if field in data:
                setattr(self, field, data[field])

    @staticmethod
    def get(short_id):
        return URLMap.query.filter_by(short=short_id).first()

    @staticmethod
    def get_or_404(short_id):
        data = URLMap.get(short_id)
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
        short_id = URLMap.__get_unique_short_id(MAX_SHORT_URL_LENGTH)
        if not URLMap.get(short_id):
            return short_id
        raise ValueError(
            'Закончились доступные адреса!'
        )

    def save(self):
        if not self.short:
            self.short = URLMap.generate_short_id()
        elif URLMap.get(self.short):
            raise ValueError(
                'Имя "{}" уже занято.'.format(self.short)
            )
        if URLMap.is_short_id_correct(self.short):
            db.session.add(self)
            db.session.commit()
            return self
        else:
            raise ValueError(
                'Указано недопустимое имя для короткой ссылки'
            )

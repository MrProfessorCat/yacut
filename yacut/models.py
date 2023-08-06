from datetime import datetime
import random
import re

from . import db
from .app_constants import (
    AVAILABLE_CHARS_FOR_SHORT_ID, MAX_SHORT_URL_LENGTH
)
from .error_handlers import NameAlreadyExists, IncorrectName


class URLMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String, nullable=False)
    short = db.Column(db.String)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    @staticmethod
    def from_dict(data):
        urlmap = URLMap()
        urlmap.original = data['url']
        urlmap.short = (
            data['custom_id'] if 'custom_id' in data and data['custom_id'] else None
        )
        return urlmap

    @staticmethod
    def get(short_id):
        return URLMap.query.filter_by(short=short_id).first()

    @staticmethod
    def get_or_404(short_id):
        return URLMap.query.filter_by(short=short_id).first_or_404()

    @staticmethod
    def is_short_id_correct(short_id):
        return (
            len(short_id) <= MAX_SHORT_URL_LENGTH and
            bool(re.fullmatch(f'[{AVAILABLE_CHARS_FOR_SHORT_ID}]+', short_id))
        )

    @staticmethod
    def generate_short_id():
        short_id = ''.join(
            random.choices(
                AVAILABLE_CHARS_FOR_SHORT_ID,
                k=MAX_SHORT_URL_LENGTH)
        )
        if not URLMap.get(short_id):
            return short_id
        raise ValueError(
            'Закончились доступные адреса!'
        )

    def save(self):
        if not self.short:
            self.short = URLMap.generate_short_id()
        elif URLMap.get(self.short):
            raise NameAlreadyExists(
                'Имя "{}" уже занято.'.format(self.short)
            )
        if URLMap.is_short_id_correct(self.short):
            db.session.add(self)
            db.session.commit()
            return self
        else:
            raise IncorrectName(
                'Указано недопустимое имя для короткой ссылки'
            )

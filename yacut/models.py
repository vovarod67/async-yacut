from datetime import datetime
from random import choice

from flask import url_for

from yacut import db
from .constants import (
    SHORT_ID_LENGTH,
    MAX_SHORT_ID_LENGTH,
    MAX_ORIGINAL_LINK_LENGTH,
    VALID_SYMBOLS,
    RESERVED_SHORT_IDS
)
from .exceptions import ShortIDAlreadyExistsError


class URLMap(db.Model):
    """Модель связи первоначального URL с коротким идентификатором."""
    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(MAX_ORIGINAL_LINK_LENGTH), nullable=False)
    short = db.Column(
        db.String(MAX_SHORT_ID_LENGTH),
        unique=True,
        nullable=False
    )
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    @staticmethod
    def get(short_id):
        """Получение объекта URLMap по короткому идентификатору"""
        return URLMap.query.filter_by(short=short_id).first()

    @classmethod
    def get_unique_short_id(cls, length=SHORT_ID_LENGTH):
        """Генерация короткого уникального идентификатора."""
        short_id = ''.join(
            choice(VALID_SYMBOLS) for _ in range(length)
        )
        if (short_id in RESERVED_SHORT_IDS or cls.get(short_id) is not None):
            return cls.get_unique_short_id(length)
        return short_id

    @staticmethod
    def create(original, custom_id=None):
        """Создание и сохранение объекта URLMap."""
        if not custom_id:
            custom_id = URLMap.get_unique_short_id()
        elif (
            custom_id in RESERVED_SHORT_IDS
            or URLMap.get(custom_id) is not None
        ):
            raise ShortIDAlreadyExistsError(
                'Предложенный вариант короткой ссылки уже существует.'
            )

        url_map = URLMap(original=original, short=custom_id)
        db.session.add(url_map)
        db.session.commit()
        return url_map

    def to_dict(self):
        """Преобразование объекта URLMap в словарь для API ответа."""
        return {
            'url': self.original,
            'short_link': url_for(
                'redirect_view',
                short_id=self.short,
                _external=True
            )
        }

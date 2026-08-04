from datetime import datetime
from string import ascii_letters, digits
from random import choice

from yacut import db


class URLMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(2048), nullable=False)
    short = db.Column(db.String(16), unique=True, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    @classmethod
    def get_unique_short_id(cls, length=6):
        short_id = ''.join(
            choice(ascii_letters + digits) for _ in range(length)
        )
        if cls.query.filter_by(short=short_id).first() is not None:
            return cls.get_unique_short_id(length)
        return short_id

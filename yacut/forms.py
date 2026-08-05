from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, MultipleFileField
from wtforms import StringField, SubmitField, URLField
from wtforms.validators import DataRequired, Length, Optional, URL, Regexp

from .constants import (
    MIN_SHORT_ID_LENGTH,
    MAX_SHORT_ID_LENGTH,
    MAX_ORIGINAL_LINK_LENGTH,
    VALID_SYMBOLS
)


class URLMapForm(FlaskForm):
    """Форма создания короткой ссылки."""

    original_link = URLField(
        'Длинная ссылка',
        validators=[
            DataRequired(message='Обязательное поле'),
            URL(message='Введите корректную ссылку'),
            Length(max=MAX_ORIGINAL_LINK_LENGTH)
        ]
    )
    custom_id = StringField(
        'Ваш вариант короткой ссылки',
        validators=[
            Length(MIN_SHORT_ID_LENGTH, MAX_SHORT_ID_LENGTH),
            Optional(),
            Regexp(
                f'^[{VALID_SYMBOLS}]+$',
                message='Указаны недопустимые символы'
            )
        ]
    )
    submit = SubmitField('Создать')


class FileForm(FlaskForm):
    """Форма загрузки файлов."""

    files = MultipleFileField(
        'Выберите файлы',
        validators=[FileRequired('Файлы не выбраны')]
    )
    submit = SubmitField('Загрузить')

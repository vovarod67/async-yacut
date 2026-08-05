from http import HTTPStatus

from flask import jsonify, request

from . import app
from .error_handlers import InvalidAPIUsage
from .models import URLMap
from .exceptions import ShortIDAlreadyExistsError
from .constants import MAX_SHORT_ID_LENGTH, VALID_SYMBOLS


@app.route('/api/id/', methods=['POST'])
def create_short_link():
    """API создание короткой ссылки."""
    data = request.get_json(silent=True)
    if data is None:
        raise InvalidAPIUsage('Отсутствует тело запроса')
    if 'url' not in data:
        raise InvalidAPIUsage('"url" является обязательным полем!')
    custom_id = data.get('custom_id')
    if (
        custom_id is not None
        and custom_id != ''
        and (
            not isinstance(custom_id, str)
            or len(custom_id) > MAX_SHORT_ID_LENGTH
            or not all(
                symbol in VALID_SYMBOLS for symbol in custom_id
            )
        )
    ):
        raise InvalidAPIUsage(
            'Указано недопустимое имя для короткой ссылки'
        )
    try:
        url_map = URLMap.create(
            original=data['url'],
            custom_id=custom_id
        )
    except ShortIDAlreadyExistsError as error:
        raise InvalidAPIUsage(str(error))
    return jsonify(url_map.to_dict()), HTTPStatus.CREATED


@app.route('/api/id/<string:short_id>/', methods=['GET'])
def get_original_link(short_id):
    """Получение первоначальной ссылки по короткому идентификатору."""
    url_map = URLMap.get(short_id)
    if url_map is None:
        raise InvalidAPIUsage('Указанный id не найден', HTTPStatus.NOT_FOUND)
    return jsonify({'url': url_map.to_dict()['url']}), HTTPStatus.OK

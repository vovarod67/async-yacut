from string import ascii_letters, digits

from flask import jsonify, request, url_for

from . import app, db
from .error_handlers import InvalidAPIUsage
from .models import URLMap


VALID_SYMBOLS = ascii_letters + digits
MAX_SHORT_ID_LENGTH = 16


@app.route('/api/id/', methods=['POST'])
def create_short_link():
    data = request.get_json(silent=True)
    if data is None:
        raise InvalidAPIUsage('Отсутствует тело запроса')
    if 'url' not in data:
        raise InvalidAPIUsage('"url" является обязательным полем!')
    custom_id = data.get('custom_id')
    if custom_id is None or custom_id == '':
        custom_id = URLMap.get_unique_short_id()
    else:
        if (
            not isinstance(custom_id, str)
            or len(custom_id) > MAX_SHORT_ID_LENGTH
            or not all(symbol in VALID_SYMBOLS for symbol in custom_id)
        ):
            raise InvalidAPIUsage(
                'Указано недопустимое имя для короткой ссылки'
            )
        if (
            custom_id == 'files'
            or URLMap.query.filter_by(short=custom_id).first() is not None
        ):
            raise InvalidAPIUsage(
                'Предложенный вариант короткой ссылки уже существует.'
            )
    url_map = URLMap(original=data['url'], short=custom_id)
    db.session.add(url_map)
    db.session.commit()
    return jsonify(
        {
            'url': url_map.original,
            'short_link': url_for(
                'redirect_view',
                short_id=url_map.short,
                _external=True
            )
        }
    ), 201


@app.route('/api/id/<string:short_id>/', methods=['GET'])
def get_original_link(short_id):
    url_map = URLMap.query.filter_by(short=short_id).first()
    if url_map is None:
        raise InvalidAPIUsage('Указанный id не найден', 404)
    return jsonify({'url': url_map.original}), 200

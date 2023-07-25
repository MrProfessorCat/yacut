from flask import request, jsonify, url_for
from http import HTTPStatus

from . import app, db
from .error_handlers import InvalidAPIUsage
from .models import URLMap
from .app_constants import MAX_SHORT_URL_LENGTH, AVAILABLE_CHARS_FOR_SHORT_ID
from .views import generate_short_id


@app.route('/api/id/', methods=('POST',))
def create_id():
    data = request.get_json()
    if not data:
        raise InvalidAPIUsage(
            'Отсутствует тело запроса',
            HTTPStatus.BAD_REQUEST
        )
    if 'url' not in data:
        raise InvalidAPIUsage(
            '"url" является обязательным полем!',
            HTTPStatus.BAD_REQUEST
        )
    if 'custom_id' in data and data['custom_id']:
        custom_id = data['custom_id']
        if URLMap.query.filter_by(short=data['custom_id']).first():
            raise InvalidAPIUsage('Имя "{}" уже занято.'.format(data['custom_id']))
        if (
            len(data['custom_id']) > MAX_SHORT_URL_LENGTH or
            set(data['custom_id']).difference(set(AVAILABLE_CHARS_FOR_SHORT_ID))
        ):
            raise InvalidAPIUsage(
                'Указано недопустимое имя для короткой ссылки',
                HTTPStatus.BAD_REQUEST
            )
    else:
        custom_id = generate_short_id()

    link = URLMap(original=data['url'], short=custom_id)
    db.session.add(link)
    db.session.commit()
    return jsonify(
        {
            'url': data['url'],
            'short_link': url_for('short_id', short_id=custom_id, _external=True)
        }
    ), HTTPStatus.CREATED


@app.route('/api/id/<string:short_id>/', methods=('GET',))
def get_url(short_id):
    data = URLMap.query.filter_by(short=short_id).first()
    if not data:
        raise InvalidAPIUsage('Указанный id не найден', HTTPStatus.NOT_FOUND)
    return jsonify({'url': data.original}), HTTPStatus.OK

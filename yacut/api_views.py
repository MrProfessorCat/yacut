from flask import request, jsonify, url_for
from http import HTTPStatus

from . import app
from .error_handlers import InvalidAPIUsage
from .models import URLMap


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
    custom_id = (
        data['custom_id'] if 'custom_id' in data and data['custom_id']
        else None
    )
    try:
        link = URLMap(original=data['url'], short=custom_id).save()
    except ValueError as error:
        raise InvalidAPIUsage(str(error))
    return jsonify(
        {
            'url': data['url'],
            'short_link': url_for('short_id', short_id=link.short, _external=True)
        }
    ), HTTPStatus.CREATED


@app.route('/api/id/<string:short_id>/', methods=('GET',))
def get_url(short_id):
    data = URLMap.get_or_404(short_id)
    return jsonify({'url': data.original}), HTTPStatus.OK

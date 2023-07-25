import random

from flask import render_template, flash, redirect

from . import app, db
from .forms import URLMapForm
from .models import URLMap
from .conf import (
    MAX_SHORT_URL_LENGTH, AVAILABLE_CHARS_FOR_SHORT_ID,
    LINK_HOST
)


def get_unique_short_id(segment_length):
    return ''.join(
        random.choice(AVAILABLE_CHARS_FOR_SHORT_ID) for _ in range(segment_length)
    )


def generate_short_id():
    short_id = get_unique_short_id(MAX_SHORT_URL_LENGTH)
    while URLMap.query.filter_by(short=short_id).first():
        short_id = get_unique_short_id(MAX_SHORT_URL_LENGTH)
    return short_id


@app.route('/', methods=('GET', 'POST'))
def index_view():
    form = URLMapForm()
    if form.validate_on_submit():
        short_id = form.custom_id.data or generate_short_id()
        if URLMap.query.filter_by(short=short_id).first():
            flash(f'Имя {short_id} уже занято!', 'validation')
            return render_template('index.html', form=form)
        link = URLMap(original=form.original_link.data, short=short_id)
        db.session.add(link)
        db.session.commit()
        flash(f'{LINK_HOST}{short_id}', 'short_id_created')
    return render_template('index.html', form=form)


@app.route('/<string:short_id>', methods=('GET',))
def short_id(short_id):
    data = URLMap.query.filter_by(short=short_id).first_or_404()
    return redirect(data.original)

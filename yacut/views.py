from flask import render_template, flash, redirect

from . import app
from .app_constants import LINK_HOST
from .error_handlers import InvalidAPIUsage
from .forms import URLMapForm
from .models import URLMap


@app.route('/', methods=('GET', 'POST'))
def index_view():
    form = URLMapForm()
    if form.validate_on_submit():
        short_id = form.custom_id.data
        if URLMap.get(short_id):
            flash(f'Имя {short_id} уже занято!', 'validation')
            return render_template('index.html', form=form)
        try:
            link = URLMap.save(form.original_link.data, form.custom_id.data)
        except InvalidAPIUsage as error:
            flash(error.message, 'validation')
            return render_template('index.html', form=form)
        flash(f'{LINK_HOST}{link.short}', 'short_id_created')
    return render_template('index.html', form=form)


@app.route('/<string:short_id>', methods=('GET',))
def short_id(short_id):
    data = URLMap.query.filter_by(short=short_id).first_or_404()
    return redirect(data.original)

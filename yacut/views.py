from flask import render_template, flash, redirect

from . import app
from .app_constants import LINK_HOST
from .forms import URLMapForm
from .models import URLMap
from .error_handlers import NameAlreadyExists, IncorrectName


@app.route('/', methods=('GET', 'POST'))
def index_view():
    form = URLMapForm()
    if form.validate_on_submit():
        short_id = form.custom_id.data
        try:
            link = URLMap(
                original=form.original_link.data,
                short=short_id).save()
        except IncorrectName as error:
            flash(str(error), 'validation')
            return render_template('index.html', form=form)
        except NameAlreadyExists:
            flash(f'Имя {short_id} уже занято!', 'validation')
            return render_template('index.html', form=form)
        flash(f'{LINK_HOST}{link.short}', 'short_id_created')
    return render_template('index.html', form=form)


@app.route('/<string:short_id>', methods=('GET',))
def short_id(short_id):
    data = URLMap.get_or_404(short_id)
    return redirect(data.original)

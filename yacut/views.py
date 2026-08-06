from flask import flash, redirect, render_template

from . import app
from .models import URLMap
from .forms import URLMapForm, FileForm
from .ydisk import async_upload_files_to_ydisk
from .exceptions import ShortIDAlreadyExistsError
from .constants import FILES_PREFIX


@app.route('/', methods=['GET', 'POST'])
def index_view():
    """Отображение формы и создание короткой ссылки."""
    form = URLMapForm()
    if not form.validate_on_submit():
        return render_template('index.html', form=form)
    try:
        url_map = URLMap.create(
            original=form.original_link.data,
            custom_id=form.custom_id.data
        )
    except ShortIDAlreadyExistsError as error:
        flash(str(error))
        return render_template('index.html', form=form)
    return render_template(
        'index.html',
        form=form,
        short_link=url_map.to_dict()['short_link']
    )


@app.route(f'/{FILES_PREFIX}', methods=['GET', 'POST'])
async def files_view():
    """Загрузка файлов на Яндекс Диск и создание коротких ссылок."""
    form = FileForm()
    if not form.validate_on_submit():
        return render_template('files.html', form=form)
    uploaded_files = await async_upload_files_to_ydisk(form.files.data)
    file_links = []
    for filename, download_link in uploaded_files:
        url_map = URLMap.create(original=download_link)
        file_links.append(
            {
                'filename': filename,
                'short_link': url_map.to_dict()['short_link']
            }
        )
    return render_template(
        'files.html',
        form=form,
        file_links=file_links
    )


@app.route('/<string:short_id>')
def redirect_view(short_id):
    """Перенаправление пользователя на первоначальный адрес."""
    url_map = URLMap.query.filter_by(short=short_id).first_or_404()
    return redirect(url_map.original)

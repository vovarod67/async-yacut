from flask import abort, flash, redirect, render_template, url_for

from . import app, db
from .models import URLMap
from .forms import URLMapForm, FileForm
from .ydisk import async_upload_files_to_ydisk


@app.route('/', methods=['GET', 'POST'])
def index_view():
    form = URLMapForm()
    if form.validate_on_submit():
        short_id = form.custom_id.data
        if (
            short_id and (
                short_id == 'files'
                or URLMap.query.filter_by(short=short_id).first() is not None
            )
        ):
            flash('Предложенный вариант короткой ссылки уже существует.')
            return render_template('index.html', form=form)
        if not short_id:
            short_id = URLMap.get_unique_short_id()
        url_map = URLMap(original=form.original_link.data, short=short_id)
        db.session.add(url_map)
        db.session.commit()
        return render_template(
            'index.html',
            form=form,
            short_link=url_for(
                'redirect_view',
                short_id=url_map.short,
                _external=True
            )
        )
    return render_template('index.html', form=form)


@app.route('/files', methods=['GET', 'POST'])
async def files_view():
    form = FileForm()
    if form.validate_on_submit():
        uploaded_files = await async_upload_files_to_ydisk(form.files.data)
        file_links = []
        for filename, download_link in uploaded_files:
            short_id = URLMap.get_unique_short_id()
            url_map = URLMap(original=download_link, short=short_id)
            db.session.add(url_map)
            file_links.append(
                {
                    'filename': filename,
                    'short_link': url_for(
                        'redirect_view',
                        short_id=short_id,
                        _external=True
                    )
                }
            )
        db.session.commit()
        return render_template(
            'files.html',
            form=form,
            file_links=file_links
        )
    return render_template('files.html', form=form)


@app.route('/<string:short_id>')
def redirect_view(short_id):
    url_map = URLMap.query.filter_by(short=short_id).first()
    if url_map is None:
        abort(404)
    return redirect(url_map.original)

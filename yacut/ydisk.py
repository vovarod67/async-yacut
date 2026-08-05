import asyncio
from urllib.parse import unquote

import aiohttp

from . import app


AUTH_HEADERS = {'Authorization': f'OAuth {app.config["DISK_TOKEN"]}'}
API_HOST = 'https://cloud-api.yandex.net/'
API_VERSION = 'v1'
REQUEST_UPLOAD_URL = f'{API_HOST}{API_VERSION}/disk/resources/upload'
DOWNLOAD_LINK_URL = f'{API_HOST}{API_VERSION}/disk/resources/download'


async def async_upload_files_to_ydisk(files):
    """Асинхронно загрузить файлы на Яндекс Диск."""
    if files is not None:
        tasks = []
        async with aiohttp.ClientSession() as session:
            for file in files:
                tasks.append(
                    asyncio.ensure_future(
                        upload_file_and_get_url(session, file)
                    )
                )
            uploaded_files = await asyncio.gather(*tasks)
        return uploaded_files


async def upload_file_and_get_url(session, file):
    """Загрузить файл на Яндекс Диск и вернуть ссылку на скачивание."""
    params = {
        'path': 'app:/' + file.filename,
        'overwrite': 'True'
    }
    async with session.get(
        REQUEST_UPLOAD_URL,
        headers=AUTH_HEADERS,
        params=params
    ) as response:
        data = await response.json()
        upload_url = data['href']
    async with session.put(
        upload_url,
        data=file.read()
    ) as response:
        location = response.headers['Location']
        location = unquote(location)
        location = location.replace('/disk', '')
    async with session.get(
        DOWNLOAD_LINK_URL,
        headers=AUTH_HEADERS,
        params={'path': location}
    ) as response:
        data = await response.json()
        download_link = data['href']
    return file.filename, download_link

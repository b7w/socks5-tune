from dataclasses import asdict
from pathlib import Path

from sanic import response
from sanic.request import Request


async def status(request: Request):
    return response.json(asdict(request.app.tunnel.status))


async def pac_profile_get(request: Request, name):
    storage_path = Path(request.app.config['STORAGE_PATH'])
    path = Path(storage_path, name)
    if path.exists():
        with path.open() as f:
            body = f.read()
            return response.text(body, headers={'Content-Type': 'application/x-ns-proxy-autoconfig'})
    return response.json(dict(msg='Not found'), 404)


async def pac_profile_post(request: Request, name):
    storage_path = Path(request.app.config['STORAGE_PATH'])
    with Path(storage_path, name).open(mode='w') as f:
        f.write(str(request.body, 'utf-8'))
        return response.json(_list_profiles(storage_path))


async def pac_profile_delete(request: Request, name):
    storage_path = Path(request.app.config['STORAGE_PATH'])
    path = Path(storage_path, name)
    if path.exists():
        path.unlink()
        return response.json(dict(msg='Ok', profiles=_list_profiles(storage_path)))
    return response.json(dict(msg='Not found', profiles=_list_profiles(storage_path)), 404)


def _list_profiles(storage_path: Path):
    return [i.name for i in storage_path.glob('*.pac')]

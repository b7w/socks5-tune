from dataclasses import asdict

from sanic import response
from sanic.request import Request

from socks5_tune.services import ProfileService


async def status(request: Request):
    return response.json(asdict(request.app.ctx.tunnel.status))


async def api_proxys_list(request: Request):
    profile_service: ProfileService = request.app.ctx.profile_service
    proxies = await profile_service.list_proxies()
    return response.json([i.as_dict() for i in proxies])


async def api_profile_list(request: Request):
    profile_service: ProfileService = request.app.ctx.profile_service
    profiles = await profile_service.list_profiles()
    return response.json([i.as_dict() for i in profiles])


async def api_profile_get(request: Request, id: int):
    profile_service: ProfileService = request.app.ctx.profile_service
    profile = await profile_service.get_profile(id)
    return response.json(profile.as_dict())


async def api_profile_delete(request: Request, id: int):
    profile_service: ProfileService = request.app.ctx.profile_service
    profile = await profile_service.delete_profile(id)
    if profile:
        return response.json(profile.as_dict())
    return response.json(dict(msg='Not found'), 404)


async def pac_profile_get(request: Request, name: str):
    profile_service: ProfileService = request.app.ctx.profile_service
    n = name.replace('.pac', '')
    body = await profile_service.find_profile_body(n)
    if body:
        return response.text(body, headers={'Content-Type': 'application/x-ns-proxy-autoconfig'})
    return response.json(dict(msg='Not found'), 404)


async def pac_profile_post(request: Request, name: str):
    profile_service: ProfileService = request.app.ctx.profile_service
    n = name.replace('.pac', '')
    if request.files:
        _, f = request.files.popitem()
        body = f[0].body
    else:
        body = request.body
    profile = await profile_service.upsert_profile(n, str(body, encoding='utf-8'))
    return response.json(profile.as_dict())

from pathlib import Path

from sanic import Sanic
from sanic.log import logger
from sanic.worker.loader import AppLoader

from socks5_tune import routes
from socks5_tune.model import TunnelInfo
from socks5_tune.tunnel import create_tunnel, stop_tunnel, healthcheck_tunnel, copy_pkey


async def before_server_start(app: Sanic, loop):
    logger.info('Starting ssh tunnel')
    healthcheck_period = int(app.config.get('HEALTHCHECK_PERIOD', '60'))
    private_key = Path(app.config.get('PRIVATE_KEY', 'None'))
    if not private_key.exists():
        logger.error(f'Private key {private_key.as_posix()} not found')
        app.stop()
    storage_path = Path(app.config.get('STORAGE_PATH', 'None'))
    if not storage_path.exists():
        logger.error(f'Storage path {storage_path.as_posix()} not found')
        app.stop()
    if ':' in app.config['DESTINATION']:
        destination, port = app.config['DESTINATION'].split(':')
    else:
        destination = app.config['DESTINATION']
        port = '22'
    ports_to_forward = [int(i) for i in str(app.config.get('PORTS_TO_FORWARD', '')).split(',') if i]
    app.ctx.tunnel = TunnelInfo()

    pkey = copy_pkey(private_key)
    loop.create_task(create_tunnel(app.ctx.tunnel, pkey, ports_to_forward, destination, int(port)))
    app.ctx.tunnel.healthcheck_task = loop.create_task(healthcheck_tunnel(app.ctx.tunnel, healthcheck_period, int(port)))


async def before_server_stop(app: Sanic, loop):
    if app.ctx.tunnel.healthcheck_task:
        logger.info('Stopping healthcheck')
        app.ctx.tunnel.healthcheck_task.cancel()
    if app.ctx.tunnel.process:
        logger.info('Stopping ssh tunnel')
        await stop_tunnel(app.ctx.tunnel.process)


def create_app() -> Sanic:
    app = Sanic('app', env_prefix='APP_')

    app.register_listener(before_server_start, 'before_server_start')
    app.register_listener(before_server_stop, 'before_server_stop')

    app.add_route(routes.status, '/status', methods=['GET'])
    app.add_route(routes.pac_profile_get, r'/profile/<name:[a-z0-9-]{2,32}.pac>', methods=['GET'])
    app.add_route(routes.pac_profile_post, r'/profile/<name:[a-z0-9-]{2,32}.pac>', methods=['POST'])
    app.add_route(routes.pac_profile_delete, r'/profile/<name:[a-z0-9-]{2,32}.pac>', methods=['DELETE'])
    return app


def main():
    loader = AppLoader(factory=create_app)
    app = loader.load()
    debug = app.config.get('DEBUG', False)
    app.prepare(host='0.0.0.0', port=9999, dev=debug)
    Sanic.serve_single(primary=app)


if __name__ == '__main__':
    main()

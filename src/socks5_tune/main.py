from pathlib import Path

from sanic import Sanic
from sanic.log import logger

from socks5_tune import routes
from socks5_tune.model import TunnelInfo
from socks5_tune.tunnel import create_tunnel, stop_tunnel, healthcheck_tunnel, copy_pkey


async def before_server_start(app: Sanic, loop):
    logger.info('Starting ssh tunnel')
    healthcheck_period = int(app.config.get('HEALTHCHECK_PERIOD', '120'))
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
    app.tunnel = TunnelInfo()

    pkey = copy_pkey(private_key)
    loop.create_task(create_tunnel(app.tunnel, pkey, destination, int(port)))
    app.tunnel.healthcheck_task = loop.create_task(healthcheck_tunnel(app.tunnel, healthcheck_period, int(port)))


async def before_server_stop(app: Sanic, loop):
    if app.tunnel.healthcheck_task:
        logger.info('Stopping healthcheck')
        app.tunnel.healthcheck_task.cancel()
    if app.tunnel.process:
        logger.info('Stopping ssh tunnel')
        await stop_tunnel(app.tunnel.process)


def main():
    app = Sanic('app', load_env='APP_')

    app.register_listener(before_server_start, 'before_server_start')
    app.register_listener(before_server_stop, 'before_server_stop')

    app.add_route(routes.status, '/status', methods=['GET'])
    app.add_route(routes.pac_profile_get, r'/profile/<name:[a-z0-9-]{2,32}.pac>', methods=['GET'])
    app.add_route(routes.pac_profile_post, r'/profile/<name:[a-z0-9-]{2,32}.pac>', methods=['POST'])
    app.add_route(routes.pac_profile_delete, r'/profile/<name:[a-z0-9-]{2,32}.pac>', methods=['DELETE'])

    debug = app.config.get('DEBUG', False)
    app.run(host='0.0.0.0', port=8000, debug=debug)


if __name__ == '__main__':
    main()

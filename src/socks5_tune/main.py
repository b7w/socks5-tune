from pathlib import Path

from sanic import Sanic
from sanic.log import logger

from socks5_tune import routes
from socks5_tune.model import TunnelInfo
from socks5_tune.tunnel import create_tunnel, stop_tunnel, copy_pkey


async def before_server_start(app: Sanic, loop):
    logger.info('Starting ssh tunnel')
    private_key = Path(app.config.get('PRIVATE_KEY', 'None'))
    if not private_key.exists():
        logger.error(f'Private key {private_key.as_posix()} not found')
        app.stop()
    storage_path = Path(app.config.get('STORAGE_PATH', 'None'))
    if not storage_path.exists():
        logger.error(f'Storage path {storage_path.as_posix()} not found')
        app.stop()
    destination = app.config['DESTINATION']
    app.tunnel = TunnelInfo()

    copy_pkey(private_key)
    task = create_tunnel(app.tunnel, destination)
    app.add_task(task)


async def before_server_stop(app: Sanic, loop):
    logger.info('Stopping ssh tunnel')
    await stop_tunnel(app.tunnel.process)


def main():
    app = Sanic('app', load_env='APP_')

    app.register_listener(before_server_start, 'before_server_start')
    app.register_listener(before_server_stop, 'before_server_stop')

    app.add_route(routes.status, '/status', methods=['GET'])
    app.add_route(routes.pac_profile_get, '/profile/<name:[a-z0-9-]{2,32}>.pac', methods=['GET'])
    app.add_route(routes.pac_profile_post, '/profile/<name:[a-z0-9-]{2,32}>.pac', methods=['POST'])
    app.add_route(routes.pac_profile_delete, '/profile/<name:[a-z0-9-]{2,32}>.pac', methods=['DELETE'])

    app.run(host='0.0.0.0', port=8000)


if __name__ == '__main__':
    main()

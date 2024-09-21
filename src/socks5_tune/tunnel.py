import asyncio
import shlex
import shutil
import signal
from asyncio.subprocess import Process
from pathlib import Path

from python_socks.async_.asyncio import Proxy
from sanic.log import logger

from socks5_tune.model import TunnelInfo


def copy_pkey(private_key):
    pkey = Path(Path.home(), '.ssh/id_rsa')
    if not pkey.exists():
        pkey.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        shutil.copy(private_key, pkey)
        pkey.chmod(0o600)
        return pkey
    else:
        logger.warn('Find existing %s, skipping copying key...', pkey.as_posix())
        return private_key


async def create_tunnel(tunnel: TunnelInfo, private_key, destination: str, port: int = 22):
    cmd = f'ssh -o StrictHostKeyChecking=no' \
          f' -i {private_key}' \
          f' -D 0.0.0.0:1080 -C -N {destination} -p {port}'
    r = None
    while r != 0:
        p = await _spawn_process(cmd)
        logger.info('Tunnel started with pid: %s', p.pid)
        tunnel.process = p
        tunnel.status.restarts += 1
        r = await p.wait()
        msg = await _proc_status(p)
        tunnel.status.last_msg = msg
        if r != 0:
            logger.warn('Tunnel daemon exit: "%s"', msg)
            await asyncio.sleep(4)
        else:
            logger.info('Tunnel daemon stopped')


async def healthcheck_tunnel(tunnel: TunnelInfo, period: int, port: int):
    await asyncio.sleep(4)
    logger.info('Starting healthcheck')
    while tunnel.healthcheck:
        if tunnel.process and tunnel.process.returncode is None:
            try:
                async def _work():
                    proxy = Proxy.from_url('socks5://127.0.0.1:1080')
                    sock = await proxy.connect(dest_host='127.0.0.1', dest_port=port)
                    reader, writer = await asyncio.open_connection(host=None, port=None, sock=sock)
                    writer.write(b'Ping\r\n')
                    await reader.read(-1)

                await asyncio.wait_for(_work(), timeout=5)
                logger.debug('Healthcheck: ok')
            except Exception as e:
                logger.warn('Healthcheck: error (%s)', e)
                tunnel.process.send_signal(signal.SIGKILL)
        await asyncio.sleep(period)


async def stop_tunnel(p: Process):
    if p:
        p.send_signal(signal.SIGTERM)
        await p.wait()
        logger.info('Tunnel stopped')


async def _spawn_process(cmd):
    bn, *args = shlex.split(cmd)
    return await asyncio.create_subprocess_exec(bn, *args, stdin=asyncio.subprocess.PIPE,
                                                stdout=asyncio.subprocess.PIPE,
                                                stderr=asyncio.subprocess.PIPE)


async def _proc_status(p: Process):
    info = str(await p.stdout.read(), encoding='utf-8')[-256:]
    error = str(await p.stderr.read(), encoding='utf-8')[-256:]
    return f'code: {p.returncode}, stdout: {info}, stderr: {error}'

from asyncio.subprocess import Process
from dataclasses import dataclass


@dataclass
class TunnelStatus:
    last_msg: str = ''
    restarts: int = 0


@dataclass
class TunnelInfo:
    healthcheck = True
    status: TunnelStatus = TunnelStatus()
    process: Process = None

from asyncio.subprocess import Process
from dataclasses import dataclass, field


@dataclass
class TunnelStatus:
    last_msg: str = ''
    restarts: int = 0


@dataclass
class TunnelInfo:
    healthcheck = True
    status: TunnelStatus = field(default_factory=TunnelStatus)
    process: Process = None

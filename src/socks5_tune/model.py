from asyncio.subprocess import Process
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from msgspec import Struct
from sqlalchemy import ForeignKey
from sqlalchemy import String, BigInteger
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship


@dataclass
class TunnelStatus:
    last_msg: str = ''
    restarts: int = 0


@dataclass
class TunnelInfo:
    healthcheck = True
    status: TunnelStatus = field(default_factory=TunnelStatus)
    process: Process = None


class ProfileType(Enum):
    RAW = "raw"
    DYNAMIC = "dynamic"


class Base(DeclarativeBase):

    def as_dict(self):
        r = {}
        for column in self.__table__.columns:
            val = getattr(self, column.name)
            if isinstance(val, Base):
                val = val.as_dict()
            if isinstance(val, Enum):
                val = val.name
            r[column.name] = val
        return r


class Profile(Base):
    __tablename__ = "profile"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    type: Mapped[ProfileType] = mapped_column()
    name: Mapped[str] = mapped_column(String(255))
    body: Mapped[Optional[str]] = mapped_column(String(32_000))

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r})"


class Proxy(Base):
    __tablename__ = "proxy"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    uri: Mapped[str] = mapped_column(String(255))

    def __repr__(self) -> str:
        return f"Proxy(id={self.id!r}, name={self.name!r}, uri={self.uri!r})"


class Domain(Base):
    __tablename__ = "domain"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    profile_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("profile.id"))
    proxy_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("proxy.id"))
    name: Mapped[str] = mapped_column(String(255))
    proxy: Mapped[Proxy] = relationship()
    wildcard: Mapped[bool] = mapped_column(default=True, doc='Some')

    def __repr__(self) -> str:
        return f"Domain(id={self.id!r}, name={self.name!r})"


class PatchRawProfile(Struct):
    body: str


class DomainCreation(Struct):
    profile_id: int
    proxy_id: int
    name: str
    wildcard: bool

from itertools import chain
from typing import Sequence, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from socks5_tune.model import Proxy, Profile, DomainCreation, Domain, ProfileType


class ProfileService:

    def __init__(self, session_maker):
        self.session_maker = session_maker

    async def list_proxies(self) -> Sequence[Proxy]:
        async with self.session_maker() as s:
            s: AsyncSession
            r = await s.execute(select(Proxy).order_by(Proxy.name))
            return r.scalars().all()

    async def list_profiles(self) -> Sequence[Profile]:
        async with self.session_maker() as s:
            s: AsyncSession
            r = await s.execute(select(Profile).order_by(Profile.name))
            return r.scalars().all()

    async def get_profile(self, pk: int) -> Profile:
        async with self.session_maker() as s:
            s: AsyncSession
            r = await s.execute(select(Profile).where(Profile.id == pk))
            return r.scalars().one()

    async def create_domain(self, domain: DomainCreation) -> Domain:
        async with self.session_maker() as s:
            s: AsyncSession
            async with s.begin():
                obj = Domain(
                    profile_id=domain.profile_id,
                    proxy_id=domain.proxy_id,
                    name=domain.name,
                    wildcard=domain.wildcard,
                )
                s.add(obj)
                return obj

    async def _find_profile(self, session: AsyncSession, name: str) -> Optional[Profile]:
        q = select(Profile).where(Profile.name == name)
        r = await session.execute(q)
        return r.scalars().one_or_none()

    async def _filter_domains(self, session: AsyncSession, profile_id: str) -> Sequence[Domain]:
        q = select(Domain) \
            .where(Domain.profile_id == profile_id) \
            .order_by(Domain.name) \
            .options(joinedload(Domain.proxy))
        r = await session.execute(q)
        return r.scalars().all()

    async def find_profile_body(self, name: str) -> str | None:
        async with self.session_maker() as s:
            s: AsyncSession
            profile = await self._find_profile(s, name)
            if not profile:
                return
            if profile.type == ProfileType.RAW:
                return profile.body
            domains = await self._filter_domains(s, profile.id)
            proxies = {i.proxy for i in domains}
            return self._template_pac(domains, proxies)

    async def upsert_profile(self, name: str, body: str) -> Profile:
        async with self.session_maker() as s, s.begin():
            s: AsyncSession
            profile = await self._find_profile(s, name)
            if not profile:
                profile = Profile(
                    type=ProfileType.RAW,
                    name=name,
                    body=body
                )
                s.add(profile)
                return profile
            if profile.type != ProfileType.RAW:
                raise Exception('Wrong profile type')
            profile.body = body
            s.add(profile)
            return profile

    async def patch_profile(self, pk: int, body: str) -> Optional[Profile]:
        async with self.session_maker() as s, s.begin():
            s: AsyncSession
            r = await s.execute(select(Profile).where(Profile.id == pk))
            profile = r.scalars().one_or_none()
            if not profile:
                return
            if profile.type != ProfileType.RAW:
                raise Exception('Wrong profile type')
            profile.body = body
            return profile

    async def delete_profile(self, pk: int) -> Optional[Profile]:
        async with self.session_maker() as s, s.begin():
            s: AsyncSession
            r = await s.execute(select(Profile).where(Profile.id == pk))
            profile = r.scalars().one_or_none()
            if not profile:
                return
            await s.delete(profile)
            return profile

    def _template_proxy(self, proxy: Proxy):
        return f'const proxy{proxy.id} = "{proxy.uri}";  // {proxy.name}'

    def _template_domain(self, domain: Domain):
        yield f'// {domain.name} -> {domain.proxy.name}'
        if domain.wildcard:
            yield f'domains.set("{domain.name}", proxy{domain.proxy_id});'
            yield f'domains.set("*.{domain.name}", proxy{domain.proxy_id});'
        else:
            yield f'domains.set("{domain.name}", proxy{domain.proxy_id});'

    def _template_pac(self, domains: Sequence[Domain], proxies: set[Proxy]):
        padding = '\n            '
        proxies_template = padding.join([self._template_proxy(i) for i in proxies])
        domains_template = padding.join(chain.from_iterable([list(self._template_domain(i)) for i in domains]))
        return f"""
        function FindProxyForURL(url, host) {{
            {proxies_template}

            const domains = new Map();
            {domains_template}

            for (const [domain, proxy] of domains.entries()) {{
                if (shExpMatch(host, domain)) {{
                    return proxy;
                }}
            }}
            return "DIRECT";
        }}
        """.strip()

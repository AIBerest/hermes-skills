"""Bounded public, same-origin reads. Not an internet-facing multi-tenant fetch proxy."""
from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlsplit

PRIVATE_PARTS = {'admin', 'account', 'dashboard', 'login', 'logout', 'auth', 'api', 'private', 'profile', 'billing', 'checkout', 'settings'}
MAX_BYTES = 2 * 1024 * 1024
MAX_REDIRECTS = 4


def validate_url(url: str, origin: str | None = None, *, allow_local: bool = False) -> str:
    p = urlsplit(url)
    if p.scheme not in ('http', 'https') or not p.hostname or p.username or p.password:
        raise ValueError('Only public HTTP(S) URLs without credentials are allowed')
    if p.query or p.fragment:
        raise ValueError('Query and fragment URLs are excluded from public audit exports')
    if any(part.lower() in PRIVATE_PARTS for part in p.path.split('/')):
        raise ValueError('Private/account/API paths are excluded')
    if origin:
        o = urlsplit(origin)
        if (p.scheme, p.hostname, p.port) != (o.scheme, o.hostname, o.port):
            raise ValueError('Cross-origin crawling/redirects are excluded')
    try:
        addresses = [ipaddress.ip_address(p.hostname)]
    except ValueError:
        addresses = [ipaddress.ip_address(x[4][0]) for x in socket.getaddrinfo(p.hostname, p.port or (443 if p.scheme == 'https' else 80), type=socket.SOCK_STREAM)]
    # Local preview is explicit and limited to loopback, never arbitrary private LANs.
    if allow_local and addresses and all(x.is_loopback for x in addresses):
        return url
    if not addresses or any(not x.is_global for x in addresses):
        raise ValueError('Non-public network address excluded')
    return url

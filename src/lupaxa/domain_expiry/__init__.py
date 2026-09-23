"""lupaxa.domain_expiry — domain name expiration lookups."""

from __future__ import annotations

from .lookup import (
    DEFAULT_TIMEOUT,
    DEFAULT_WARN_DAYS,
    ExpiryResult,
    lookup,
    query_whois,
)
from .version import __version__, get_version

__all__ = [
    "DEFAULT_TIMEOUT",
    "DEFAULT_WARN_DAYS",
    "ExpiryResult",
    "__version__",
    "get_version",
    "lookup",
    "query_whois",
]

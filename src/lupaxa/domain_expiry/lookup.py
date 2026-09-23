"""WHOIS expiration lookup for one domain name."""

from __future__ import annotations

import math
import socket
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, date, datetime
from typing import Literal

import whois
from tld import get_tld

DEFAULT_TIMEOUT = 10.0
DEFAULT_WARN_DAYS = 30

Status = Literal["expires", "available", "unpublished", "invalid", "error"]
WhoisQuery = Callable[[str, float], object]

_NOT_REGISTERED = (
    "no match",
    "not found",
    "no entries found",
    "no data found",
)


@dataclass(frozen=True)
class ExpiryResult:
    """WHOIS expiration lookup for one domain."""

    domain: str
    status: Status
    expiration: datetime | None = None
    days_remaining: int | None = None
    error: str | None = None


def query_whois(domain: str, timeout: float) -> object:
    """Query WHOIS for ``domain`` and restore the process socket timeout."""
    previous = socket.getdefaulttimeout()
    socket.setdefaulttimeout(timeout)
    try:
        record: object = whois.whois(domain)
    finally:
        socket.setdefaulttimeout(previous)
    return record


def lookup(
    domain: str,
    *,
    timeout: float = DEFAULT_TIMEOUT,
    now: datetime | None = None,
    whois_query: WhoisQuery | None = None,
) -> ExpiryResult:
    """Return the expiration status of one domain name.

    Parameters
    ----------
    domain:
        Hostname to look up. International names are converted to ASCII.
    timeout:
        Socket timeout in seconds for the WHOIS query. Must be greater than 0.
    now:
        Clock used for ``days_remaining``. Defaults to the current UTC time.
    whois_query:
        Callable ``(domain, timeout) -> record``. Defaults to :func:`query_whois`.

    Returns
    -------
    ExpiryResult
        ``expires`` when a date is published, ``available`` when the registry
        reports no registration, ``unpublished`` when the lookup succeeds
        without a date, ``invalid`` when the name is not a domain, or
        ``error`` when the query fails.

    Raises
    ------
    ValueError
        If ``timeout`` is not greater than 0.
    """
    _require_timeout(timeout)
    try:
        normalized = _require_domain(domain)
    except ValueError:
        shown = domain.strip() or domain
        return ExpiryResult(shown, "invalid")
    moment = _as_utc(now or datetime.now(UTC))
    query = whois_query or query_whois
    try:
        record = query(normalized, timeout)
    except Exception as exc:
        if _is_not_registered(exc):
            return ExpiryResult(normalized, "available")
        return ExpiryResult(normalized, "error", error=_error_text(exc))
    expiration = _expiration_from(record)
    if expiration is None:
        return ExpiryResult(normalized, "unpublished")
    expiration = _as_utc(expiration)
    remaining = (expiration.date() - moment.date()).days
    return ExpiryResult(
        normalized,
        "expires",
        expiration=expiration,
        days_remaining=remaining,
    )


def _require_domain(domain: str) -> str:
    value = domain.strip().lower().rstrip(".")
    if not value or any(char in value for char in " /\\:@?#"):
        raise ValueError("domain must be a hostname")
    try:
        ascii_name = value.encode("idna").decode("ascii")
    except UnicodeError as exc:
        raise ValueError("domain must be a hostname") from exc
    labels = ascii_name.split(".")
    if len(labels) < 2 or any(not _is_label(label) for label in labels):
        raise ValueError("domain must be a hostname")
    if len(ascii_name) > 253:
        raise ValueError("domain must be a hostname")
    if get_tld(ascii_name, fix_protocol=True, fail_silently=True) is None:
        raise ValueError(f"invalid domain: {ascii_name}")
    return ascii_name


def _is_label(label: str) -> bool:
    if not label or len(label) > 63 or label.startswith("-") or label.endswith("-"):
        return False
    return all(char.isalnum() or char == "-" for char in label)


def _require_timeout(timeout: float) -> float:
    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("timeout must be greater than 0")
    return timeout


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def _expiration_from(record: object) -> datetime | None:
    raw = getattr(record, "expiration_date", None)
    values = raw if isinstance(raw, list) else (raw,)
    parsed = [item for item in (_coerce_datetime(value) for value in values) if item]
    if not parsed:
        return None
    return min(_as_utc(item) for item in parsed)


def _coerce_datetime(value: object) -> datetime | None:
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime(value.year, value.month, value.day, tzinfo=UTC)
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        try:
            return datetime.fromisoformat(text.replace("Z", "+00:00"))
        except ValueError:
            return None
    return None


def _is_not_registered(exc: BaseException) -> bool:
    text = str(exc).casefold()
    return any(marker in text for marker in _NOT_REGISTERED)


def _error_text(exc: BaseException) -> str:
    text = str(exc).strip() or exc.__class__.__name__
    return " ".join(text.split())

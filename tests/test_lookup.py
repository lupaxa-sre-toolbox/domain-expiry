"""WHOIS expiration lookup."""

from __future__ import annotations

import socket
from datetime import UTC, date, datetime

import pytest
import whois

from lupaxa.domain_expiry.lookup import WhoisQuery, lookup


class _Record:
    def __init__(self, expiration_date: object) -> None:
        self.expiration_date = expiration_date


def _query(record: object) -> WhoisQuery:
    def inner(_domain: str, _timeout: float) -> object:
        return record

    return inner


def test_uses_earliest_expiration() -> None:
    later = datetime(2028, 1, 1, tzinfo=UTC)
    earlier = datetime(2027, 3, 15, tzinfo=UTC)
    result = lookup(
        "Example.COM.",
        now=datetime(2026, 9, 22, tzinfo=UTC),
        whois_query=_query(_Record([later, earlier, "not-a-date"])),
    )
    assert result.domain == "example.com"
    assert result.status == "expires"
    assert result.expiration == earlier
    assert result.days_remaining == 174


def test_naive_and_date_values_are_utc() -> None:
    result = lookup(
        "example.org",
        now=datetime(2026, 9, 22, 23, 30, tzinfo=UTC),
        whois_query=_query(_Record(date(2026, 9, 23))),
    )
    assert result.days_remaining == 1
    assert result.expiration is not None
    assert result.expiration.tzinfo is UTC


def test_unpublished_when_date_missing() -> None:
    result = lookup("example.net", whois_query=_query(_Record(None)))
    assert result.status == "unpublished"
    assert result.expiration is None
    assert result.days_remaining is None


def test_available_when_registry_reports_no_match() -> None:
    def query(_domain: str, _timeout: float) -> object:
        raise RuntimeError("No match for domain")

    result = lookup("missing.com", whois_query=query)
    assert result.status == "available"
    assert result.error is None


def test_error_keeps_the_message() -> None:
    def query(_domain: str, _timeout: float) -> object:
        raise TimeoutError("timed   out")

    result = lookup("slow.com", whois_query=query)
    assert result.status == "error"
    assert result.error == "timed out"


def test_invalid_domain_is_a_result_and_skips_whois() -> None:
    def query(_domain: str, _timeout: float) -> object:
        raise AssertionError("invalid names are not queried")

    result = lookup("https://example.com", whois_query=query)
    assert result.status == "invalid"
    assert result.domain == "https://example.com"
    result = lookup("  example.bobthrfish  ", whois_query=query)
    assert result.status == "invalid"
    assert result.domain == "example.bobthrfish"
    with pytest.raises(ValueError, match="timeout"):
        lookup("example.com", timeout=0, whois_query=query)


def test_query_whois_restores_socket_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    def boom(_domain: str) -> object:
        raise TimeoutError("timed out")

    monkeypatch.setattr(whois, "whois", boom)
    before = socket.getdefaulttimeout()
    try:
        result = lookup("example.com", timeout=1.5)
    finally:
        socket.setdefaulttimeout(before)
    assert socket.getdefaulttimeout() == before
    assert result.status == "error"
    assert result.error == "timed out"

"""Command-line interface."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from lupaxa.domain_expiry.cli import (
    expand_domains,
    format_expiration,
    format_table,
    main,
    read_domains,
)
from lupaxa.domain_expiry.lookup import ExpiryResult


def _expires(domain: str, days: int) -> ExpiryResult:
    expiration = datetime(2026, 9, 22, tzinfo=UTC)
    return ExpiryResult(domain, "expires", expiration=expiration, days_remaining=days)


def test_format_table() -> None:
    when = datetime(2026, 1, 2, tzinfo=UTC)
    table = format_table(
        [
            _expires("example.com", 2),
            ExpiryResult("example.com", "expires", expiration=when, days_remaining=-3),
            ExpiryResult("free.test", "available"),
            ExpiryResult("hidden.test", "unpublished"),
            ExpiryResult("slow.test", "error", error="timed out"),
        ]
    )
    assert table.splitlines() == [
        "+-------------+---------------------+------+",
        "| Domain      | Date                | Days |",
        "+-------------+---------------------+------+",
        "| example.com | 22nd September 2026 |    2 |",
        "| example.com | Expired             |   -3 |",
        "| free.test   | Available           |    — |",
        "| hidden.test | unpublished         |    — |",
        "| slow.test   | timed out           |    — |",
        "+-------------+---------------------+------+",
    ]


def test_ordinal_dates() -> None:
    assert format_expiration(datetime(2026, 11, 11, tzinfo=UTC), 10) == "11th November 2026"
    assert format_expiration(datetime(2026, 1, 1, tzinfo=UTC), 1) == "1st January 2026"
    assert format_expiration(datetime(2026, 1, 2, tzinfo=UTC), 1) == "2nd January 2026"
    assert format_expiration(datetime(2026, 1, 3, tzinfo=UTC), 1) == "3rd January 2026"
    assert format_expiration(datetime(2026, 11, 12, tzinfo=UTC), 1) == "12th November 2026"
    assert format_expiration(datetime(2026, 11, 13, tzinfo=UTC), 1) == "13th November 2026"
    assert format_expiration(datetime(2026, 1, 2, tzinfo=UTC), -3) == "Expired"


def test_read_domains_skips_comments(tmp_path: Path) -> None:
    path = tmp_path / "domains.txt"
    path.write_text("# note\n\nexample.com  # prod\n", encoding="utf-8")
    assert read_domains(str(path)) == ["example.com"]


def test_help_version_and_missing_domain(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--help"]) == 0
    help_text = capsys.readouterr().out
    assert "DOMAIN" in help_text
    assert main(["--version"]) == 0
    assert capsys.readouterr().out.strip()
    assert main([]) == 2
    assert "usage:" in capsys.readouterr().out.lower()


def test_multiple_domains(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    seen: list[str] = []

    def fake(domain: str, **_kwargs: object) -> ExpiryResult:
        seen.append(domain)
        return _expires(domain, 90)

    monkeypatch.setattr("lupaxa.domain_expiry.cli.lookup", fake)
    assert main(["example.com", "example.org", "example.net"]) == 0
    assert seen == ["example.com", "example.org", "example.net"]
    output = capsys.readouterr().out
    assert output.splitlines() == [
        "+-------------+---------------------+------+",
        "| Domain      | Date                | Days |",
        "+-------------+---------------------+------+",
        "| example.com | 22nd September 2026 |   90 |",
        "| example.org | 22nd September 2026 |   90 |",
        "| example.net | 22nd September 2026 |   90 |",
        "+-------------+---------------------+------+",
    ]
    assert expand_domains(["example.com,example.org", " example.net "]) == [
        "example.com",
        "example.org",
        "example.net",
    ]


def test_bad_timeout_and_warn_days() -> None:
    assert main(["example.com", "--timeout", "0"]) == 2
    assert main(["example.com", "--timeout", "nope"]) == 2
    assert main(["example.com", "--warn-days", "-1"]) == 2


def test_exit_codes(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    answers = {
        "safe.example": _expires("safe.example", 90),
        "soon.example": _expires("soon.example", 30),
        "free.example": ExpiryResult("free.example", "available"),
        "slow.example": ExpiryResult("slow.example", "error", error="timed out"),
    }

    def fake(domain: str, **_kwargs: object) -> ExpiryResult:
        return answers[domain]

    monkeypatch.setattr("lupaxa.domain_expiry.cli.lookup", fake)
    assert main(["safe.example"]) == 0
    assert "Domain" in capsys.readouterr().out
    assert main(["soon.example", "--warn-days", "30"]) == 1
    assert main(["soon.example", "--warn-days", "29"]) == 0
    assert main(["free.example"]) == 1
    assert main(["slow.example"]) == 2
    assert main(["soon.example", "slow.example"]) == 1


def test_file_domains(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    path = tmp_path / "domains.txt"
    path.write_text("safe.example\n", encoding="utf-8")
    monkeypatch.setattr(
        "lupaxa.domain_expiry.cli.lookup",
        lambda domain, **_kwargs: _expires(domain, 90),
    )
    assert main(["--file", str(path)]) == 0
    assert "safe.example" in capsys.readouterr().out


def test_invalid_and_timeout_stay_in_the_table(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def fake(domain: str, **_kwargs: object) -> ExpiryResult:
        if domain == "slow.com":
            return ExpiryResult(domain, "error", error="connect timed out")
        return ExpiryResult(domain, "invalid")

    monkeypatch.setattr("lupaxa.domain_expiry.cli.lookup", fake)
    assert main(["slow.com", "example.bobthrfish", "not a domain"]) == 1
    captured = capsys.readouterr()
    assert captured.err == ""
    lines = captured.out.splitlines()
    assert "| slow.com           | connect timed out |    — |" in lines
    assert "| example.bobthrfish | Invalid Domain    |    — |" in lines
    assert "| not a domain       | Invalid Domain    |    — |" in lines


def _row_domains(output: str) -> list[str]:
    names: list[str] = []
    for line in output.splitlines():
        if line.startswith("| ") and not line.startswith("| Domain"):
            names.append(line.split("|")[1].strip())
    return names


def test_sort_is_alphabetical(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(
        "lupaxa.domain_expiry.cli.lookup",
        lambda domain, **_kwargs: _expires(domain, 90),
    )
    assert main(["example.org", "Example.com", "--sort", "domain"]) == 0
    lines = capsys.readouterr().out.splitlines()
    assert lines.index("| Example.com | 22nd September 2026 |   90 |") < lines.index(
        "| example.org | 22nd September 2026 |   90 |"
    )
    assert main(["example.org", "Example.com", "--sort", "domain", "--order", "desc"]) == 0
    lines = capsys.readouterr().out.splitlines()
    assert lines.index("| example.org | 22nd September 2026 |   90 |") < lines.index(
        "| Example.com | 22nd September 2026 |   90 |"
    )


def test_sort_by_date_and_days(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    later = ExpiryResult(
        "later.com",
        "expires",
        expiration=datetime(2027, 3, 1, tzinfo=UTC),
        days_remaining=100,
    )
    sooner = ExpiryResult(
        "sooner.com",
        "expires",
        expiration=datetime(2026, 6, 1, tzinfo=UTC),
        days_remaining=10,
    )
    gone = ExpiryResult(
        "gone.com",
        "expires",
        expiration=datetime(2025, 1, 1, tzinfo=UTC),
        days_remaining=-20,
    )
    free = ExpiryResult("free.com", "available")
    answers = {item.domain: item for item in (later, sooner, gone, free)}

    def fake(domain: str, **_kwargs: object) -> ExpiryResult:
        return answers[domain]

    monkeypatch.setattr("lupaxa.domain_expiry.cli.lookup", fake)
    names = ["later.com", "sooner.com", "gone.com", "free.com"]

    assert main([*names, "--sort", "date"]) == 1
    assert _row_domains(capsys.readouterr().out) == [
        "gone.com",
        "sooner.com",
        "later.com",
        "free.com",
    ]
    assert main([*names, "--sort", "date", "--order", "descending"]) == 1
    assert _row_domains(capsys.readouterr().out) == [
        "later.com",
        "sooner.com",
        "gone.com",
        "free.com",
    ]
    assert main([*names, "--sort", "days", "--order", "ascending"]) == 1
    assert _row_domains(capsys.readouterr().out) == [
        "gone.com",
        "sooner.com",
        "later.com",
        "free.com",
    ]
    assert main([*names, "--sort", "days", "--order", "descending"]) == 1
    assert _row_domains(capsys.readouterr().out) == [
        "later.com",
        "sooner.com",
        "gone.com",
        "free.com",
    ]


def test_sort_usage(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["example.bobthrfish", "--order", "descending"]) == 2
    assert "--order requires --sort" in capsys.readouterr().err
    assert main(["example.bobthrfish", "--sort", "weeks"]) == 2
    assert main(["example.bobthrfish", "--sort", "days", "--order", "sideways"]) == 2


def test_missing_file() -> None:
    assert main(["--file", "does-not-exist.txt"]) == 2

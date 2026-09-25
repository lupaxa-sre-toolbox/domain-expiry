# Reference

## Commands

| Command                          | Role                                     |
| :------------------------------- | :--------------------------------------- |
| `domain-expiry`                  | The installed command                    |
| `python -m lupaxa.domain_expiry` | The same program, run as a Python module |

## CLI Arguments

| Flag                | Default   | Description                                          |
| :------------------ | :-------- | :--------------------------------------------------- |
| `DOMAIN`            | optional  | Domain name; repeat for more than one                |
| `--file`, `-f`      | none      | Text file of names, one per line; `-` reads stdin    |
| `--timeout`, `-t`   | `10`      | WHOIS socket timeout in seconds                      |
| `--warn-days`, `-w` | `30`      | Exit `1` when a domain expires within this many days |
| `--sort`, `-s`      | none      | Sort by `domain`, `date`, or `days`                  |
| `--order`           | ascending | `ascending` or `descending`; requires `--sort`       |
| `--version`         | —         | Print the package version and exit                   |

`--timeout` must be greater than `0`. `--warn-days` must be `0` or greater.
`--order` accepts `ascending`, `descending`, `asc`, or `desc`.
Pass several names as separate arguments, or separate them with commas.
With no domains, the command prints the same text as `--help` and exits `2`.

## Exit Codes

| Code | When                                                                               |
| :--- | :--------------------------------------------------------------------------------- |
| `0`  | Help, version, or every domain has a published date further out than `--warn-days` |
| `1`  | A domain is due, expired, available, unpublished, or invalid                       |
| `2`  | Usage failed, a file could not be read, no domains were given, or a query failed   |

When one domain needs attention and another query fails, the command exits
`1`.

## Library

| Name                | Meaning                                                    |
| :------------------ | :--------------------------------------------------------- |
| `lookup`            | Look up one domain and return an `ExpiryResult`            |
| `query_whois`       | Query WHOIS and restore the process socket timeout         |
| `ExpiryResult`      | Frozen result: domain, status, expiration, days, and error |
| `DEFAULT_TIMEOUT`   | Default WHOIS timeout (`10.0` seconds)                     |
| `DEFAULT_WARN_DAYS` | Default warning window (`30` days)                         |
| `get_version()`     | Return the package version string                          |

`status` is `expires`, `available`, `unpublished`, `invalid`, or `error`.
`days_remaining` is set only for `expires`. It is the difference of the UTC
calendar dates, so a date later today is `0`. `error` is set only for
`error`, and is a single line.

An empty name, a non-hostname, or an unknown top-level domain is `invalid`
and is not queried. A non-positive timeout raises `ValueError`.
A registry "no match" style failure is `available`, not `error`.

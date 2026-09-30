<p align="center">
  <a href="https://github.com/lupaxa-sre-toolbox">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/organisations/sre-toolbox/readme-logo.png" alt="SRE Toolbox" />
  </a>
</p>

<h1 align="center">Domain Expiry</h1>

Look up domain name expiration dates over WHOIS.

Requires Python 3.13 or newer and outbound access to the registry WHOIS
servers. `python-whois`, `prettytable`, and `tld` are installed with the
package.

## Install

```bash
pip install lupaxa-domain-expiry
domain-expiry --help
```

## CLI

```bash
domain-expiry example.com example.org
domain-expiry example.com,example.org
domain-expiry --file domains.txt --warn-days 14
domain-expiry --file - --timeout 5
domain-expiry --sort days --order descending example.com example.org
python -m lupaxa.domain_expiry --version
```

Pass several names as separate arguments, or separate them with commas.
`--file` reads one name per line. Blank lines and `#` comments are ignored.
`-` reads stdin. Repeat `--file` to combine lists. Names on the command line
are checked first, then names from each file. With no domains, the command
prints help and exits `2`.

| Flag                | Default   | Description                                          |
| :------------------ | :-------- | :--------------------------------------------------- |
| `DOMAIN`            | optional  | Domain name; repeat for more than one                |
| `--file`, `-f`      | none      | Text file of names, one per line; `-` reads stdin    |
| `--timeout`, `-t`   | `10`      | WHOIS socket timeout in seconds                      |
| `--warn-days`, `-w` | `30`      | Exit `1` when a domain expires within this many days |
| `--sort`, `-s`      | none      | Sort by `domain`, `date`, or `days`                  |
| `--order`           | ascending | `ascending` or `descending`; requires `--sort`       |
| `--version`         | —         | Print the package version and exit                   |

`--timeout` must be greater than `0`. `--warn-days` must be `0` or greater,
and the comparison is inclusive: `30` days left exits `1` when `--warn-days`
is `30`. `--warn-days 0` exits `1` for names that expire today or are already
expired. `--order` accepts `ascending`, `descending`, `asc`, or `desc`.
`--order` without `--sort` exits `2`.

`--sort` orders the table by domain, date, or days. Domain order is
alphabetical and ignores case. Date order uses the expiration date, including
names that show `Expired`. Day order uses the day count. Rows with no date or
day count stay at the end. Without `--sort`, rows stay in the order the names
were given.

## Output

Every name is a row, including invalid names and timeouts.

```text
+--------------+---------------------+------+
| Domain       | Date                | Days |
+--------------+---------------------+------+
| example.com  | 15th March 2027     |  174 |
| example.com  | 22nd September 2026 |    0 |
| example.com  | Expired             |  -12 |
| missing.test | Available           |    — |
| example.net  | unpublished         |    — |
| slow.test    | timed out           |    — |
| nope.invalid | Invalid Domain      |    — |
+--------------+---------------------+------+
```

A published date is the day, with `st`, `nd`, `rd`, or `th`, then the full
month name and the year, as in `11th November 2026`. `Expired` means that
date is already past. `Days` is the number of UTC calendar days remaining.
`0` means the name expires today. A negative number is how many days ago it
expired.

`Available` means the registry has no registration. `unpublished` means the
lookup succeeded but WHOIS included no date, which is common when a registry
redacts the record. `Invalid Domain` means the name was not queried: it is
empty, not a hostname, or its suffix is not a known top-level domain. A query
failure, including a connection timeout, puts the error in the date column.

International names are converted to ASCII before the query, and that form is
what the domain column prints.

## Exit Codes

| Code | When                                                                               |
| :--- | :--------------------------------------------------------------------------------- |
| `0`  | Help, version, or every domain has a published date further out than `--warn-days` |
| `1`  | A domain is due, expired, available, unpublished, or invalid                       |
| `2`  | Usage failed, a file could not be read, no domains were given, or a query failed   |

When one domain needs attention and another query fails, the command exits
`1`.

## Library

```python
from lupaxa.domain_expiry import lookup

result = lookup("example.com", timeout=10.0)
if result.status == "expires":
    print(result.expiration, result.days_remaining)
else:
    print(result.status, result.error)
```

`lookup` returns one `ExpiryResult` for a registry miss, an unpublished date,
an invalid name, or a query failure, including a connection timeout. `status`
is `expires`, `available`, `unpublished`, `invalid`, or `error`.
`days_remaining` is set only for `expires`. It is the difference of the UTC
calendar dates, so a date later today is `0`. `error` is set only for
`error`, and is a single line.

An empty name, a non-hostname, or an unknown top-level domain is `invalid`
and is not sent to WHOIS. A non-positive timeout raises `ValueError`. A
registry "no match" style failure is `available`, not `error`. Tests can pass
`whois_query` to replace the network call. Naive datetimes are treated as UTC,
and the earliest expiration date is kept.

`query_whois` runs the WHOIS query and restores the process socket timeout.
`DEFAULT_TIMEOUT` is `10.0` seconds. `DEFAULT_WARN_DAYS` is `30`.
`get_version()` returns the package version string.

## Development

```bash
make init
make python-install-dev
make python-check
```

<a href="https://github.com/the-lupaxa-project">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/components/footer-for-child-orgs.svg" alt="The Lupaxa Project Footer" width="100%" />
</a>

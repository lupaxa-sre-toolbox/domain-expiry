# Usage

## Output

Results print as one table.

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

A published date is the day, with `st`, `nd`, `rd`, or `th`, then the month
name and the year, as in `11th November 2026`. `Expired` means that date is
already past. `Days` is the number of UTC calendar days remaining. `0` means
the name expires today. A negative number is how many days ago it expired.

`Available` means the registry has no registration. `unpublished` means the
lookup succeeded but WHOIS included no date, which is common when a registry
redacts the record. `Invalid Domain` means the name was not queried: it is
empty, not a hostname, or its suffix is not a known top-level domain. A query
failure, including a connection timeout, puts the error in the date column.
Every name is a row.

International names are converted to ASCII before the query, and that form is
what the domain column prints.

## CLI

```bash
domain-expiry example.com example.org example.net
domain-expiry example.com,example.org
domain-expiry --file domains.txt --warn-days 14
domain-expiry --file - --timeout 5
domain-expiry --sort domain example.org example.com
domain-expiry --sort days --order descending example.com example.org
```

With no domains, the command prints help and exits `2`.

`--file` reads one domain per line. Blank lines and `#` comments are ignored.
`-` reads stdin. Repeat `--file` to combine lists. Names on the command line
are checked first, then names from each file.

`--timeout` is the socket timeout for that WHOIS query, in seconds. It must
be greater than `0`.

`--warn-days` is how close a date can be before the command exits `1`. The
comparison is inclusive: a domain with `30` days left exits `1` when
`--warn-days` is `30`. `0` means only today or earlier. Available,
unpublished, expired, and invalid names also exit `1`. A failed query,
including a timeout, exits `2`. When one name needs attention and another
query fails, the command exits `1`.

`--sort` orders the table by `domain`, `date`, or `days`. `--order` is
`ascending` (the default) or `descending`. `asc` and `desc` are accepted.
Domain order is alphabetical and ignores case. Date order uses the expiration
date, including names that show `Expired`. Day order uses the day count.
Rows with no date or day count stay at the end. Without `--sort`, rows stay
in the order the names were given. `--order` without `--sort` exits `2`.

## Library

```python
from lupaxa.domain_expiry import lookup

result = lookup("example.com", timeout=10.0)
if result.status == "expires":
    print(result.expiration, result.days_remaining)
else:
    print(result.status, result.error)
```

`lookup` returns a result for registry misses, unpublished dates, invalid
names, and query failures, including a connection timeout. An invalid name
has status `invalid` and is not sent to WHOIS. It raises `ValueError` when
`timeout` is not greater than `0`.

Pass `whois_query` to replace the network call in tests. The callable receives
the ASCII domain and the timeout in seconds, and returns an object with an
`expiration_date` attribute. That attribute may be a `datetime`, a `date`, an
ISO-8601 string, or a list of those. The earliest date is kept. Naive values
are treated as UTC.

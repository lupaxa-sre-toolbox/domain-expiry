# Examples

## One Domain

```bash
domain-expiry example.com
```

## Several Names

```bash
domain-expiry example.com example.org example.net
```

## A List on Disk

`domains.txt`:

```text
# production
example.com
example.org
```

```bash
domain-expiry --file domains.txt --warn-days 14
```

## Names from Another Command

```bash
printf '%s\n' example.com example.org | domain-expiry --file -
```

## Sorted Table

```bash
domain-expiry --sort days --order descending example.com example.org example.net
```

## Shorter Timeout

```bash
domain-expiry example.com --timeout 5
```

## Library

```python
from datetime import UTC, datetime

from lupaxa.domain_expiry import lookup

result = lookup("example.com", timeout=5.0, now=datetime.now(UTC))
print(result.domain, result.status, result.days_remaining)
```

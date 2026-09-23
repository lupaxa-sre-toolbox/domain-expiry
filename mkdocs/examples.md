# Examples

## One domain

```bash
domain-expiry example.com
```

## Several names

```bash
domain-expiry example.com example.org example.net
```

## A list on disk

`domains.txt`:

```text
# production
example.com
example.org
```

```bash
domain-expiry --file domains.txt --warn-days 14
```

## Names from another command

```bash
printf '%s\n' example.com example.org | domain-expiry --file -
```

## Sorted table

```bash
domain-expiry --sort days --order descending example.com example.org example.net
```

## Shorter timeout

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

# Domain Expiry

`lupaxa-domain-expiry` looks up when a domain name expires. It asks WHOIS for
the expiration date and prints how many days remain.

```bash
pip install lupaxa-domain-expiry
domain-expiry example.com
```

Results print as a table with the domain, the date, and the days remaining.
Every name is a row. A past date shows `Expired`. A name the registry does
not know shows `Available`. A lookup that succeeds without a date shows
`unpublished`. A name that is not a domain shows `Invalid Domain`. A query
failure, including a connection timeout, shows the error in the date column.

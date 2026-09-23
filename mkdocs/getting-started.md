# Getting started

## Requirements

- Python 3.13 or newer
- Outbound access to the registry WHOIS servers for the names you look up
- The `python-whois`, `prettytable`, and `tld` packages, installed with this distribution

## Install

```bash
pip install lupaxa-domain-expiry
domain-expiry --help
```

## First run

```bash
domain-expiry example.com example.org
```

Every name is a row in the table. A date further out than `--warn-days`
(default 30) is a quiet success. A name that is due sooner, already expired,
available, invalid, or missing a published date makes the command exit `1`.

Module entry point:

```bash
python -m lupaxa.domain_expiry --version
```

### From source (development)

```bash
make init
make python-install-dev
domain-expiry --version
```

## Makefile helpers

```bash
make python-check
make mkdocs-serve
```

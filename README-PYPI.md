<!-- markdownlint-disable -->
<p align="center">
  <a href="https://github.com/lupaxa-sre-toolbox">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/organisations/sre-toolbox/readme-logo.png" alt="Project Logo" width="256"/><br/>
  </a>
</p>
<h3 align="center">
  The Lupaxa SRE Toolbox<br />
  Part of The Lupaxa Project
</h3>

<br />

# lupaxa-domain-expiry

Look up domain name expiration dates over WHOIS.

## Features

- Query one or more domain names and print one table
- Read names from a file, or from stdin with `--file -`
- Report the expiration date and the number of days remaining
- Keep every name in the table, including invalid names and timeouts
- Treat a missing registration as available
- Treat a successful lookup with no date as unpublished
- Keep query failures separate from missing dates
- Exit `1` when a domain is due within `--warn-days`
- Sort the table by domain, date, or days, ascending or descending
- Use the `lookup` library API
- Depend on `python-whois`, `prettytable`, and `tld` at runtime

## Installation

### From PyPI

```bash
pip install lupaxa-domain-expiry
```

### From source (development mode)

```bash
pip install -e ".[dev]"
```

Requires Python 3.13+.

## Library quick start

```python
from lupaxa.domain_expiry import lookup

result = lookup("example.com", timeout=10.0)
print(result.domain, result.status, result.days_remaining)
```

## CLI quick start

```bash
domain-expiry --help
domain-expiry example.com example.org
domain-expiry --file domains.txt --warn-days 14 --timeout 5
```

You can also run the CLI as a module:

```bash
python -m lupaxa.domain_expiry --help
python -m lupaxa.domain_expiry --version
```

## Options

- `DOMAIN`: one or more domain names
- `--file`, `-f`: text file of domain names, one per line; `-` reads stdin
- `--timeout`, `-t`: WHOIS socket timeout in seconds; default `10`
- `--warn-days`, `-w`: exit `1` when a domain expires within this many days; default `30`
- `--sort`, `-s`: sort by `domain`, `date`, or `days`
- `--order`: `ascending` or `descending` (default `ascending`); requires `--sort`
- `--version`: print the package version

## Documentation

Online documentation:

[Documentation](https://domain-expiry.thelupaxaproject.org/)

Source repository:

[GitHub](https://github.com/lupaxa-sre-toolbox/domain-expiry)

### Serve docs locally

From a clone of the repository:

```bash
make mkdocs-serve
```

Then open the local URL printed by MkDocs in your browser.

## Development

Clone the repository and install with Make:

```bash
make init                # first-time makefile-skills checkout
make python-install-dev  # editable install with [dev]
make python-check        # lint, type-check, and test
```

<a href="https://github.com/the-lupaxa-project">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/components/footer-for-child-orgs.svg" alt="The Lupaxa Project Footer" width="100%" />
</a>

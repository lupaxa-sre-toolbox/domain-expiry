<p align="center">
  <a href="https://github.com/lupaxa-sre-toolbox">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/organisations/sre-toolbox/readme-logo.png" alt="SRE Toolbox" />
  </a>
</p>

<h1 align="center">Domain Expiry</h1>

Look up domain name expiration dates over WHOIS.

## Install

```bash
pip install lupaxa-domain-expiry
domain-expiry --help
```

## CLI

```bash
domain-expiry example.com example.org
domain-expiry --file domains.txt --warn-days 14
python -m lupaxa.domain_expiry --version
```

Results print as a table with domain, date, and days columns. Every name is
a row, including invalid names and timeouts. The command exits `1` when a
name is due within `--warn-days` (default 30), already expired, available,
invalid, or has no published date. `--sort domain`, `--sort date`, or
`--sort days` orders the table. `--order descending` reverses that order.

## Library

```python
from lupaxa.domain_expiry import lookup

result = lookup("example.com")
print(result.status, result.expiration, result.days_remaining)
```

## Development

```bash
make init
make python-install-dev
make python-check
make mkdocs-serve
```

## Documentation

The published guide is at
<https://domain-expiry.thelupaxaproject.org/>.

Site Markdown lives in `mkdocs/`.

<a href="https://github.com/the-lupaxa-project">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/components/footer-for-child-orgs.svg" alt="The Lupaxa Project Footer" width="100%" />
</a>

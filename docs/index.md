# loopia-python

A Python client library for the [Loopia](https://www.loopia.com) domain registrar API.

## Installation

```bash
pip install loopiase
```

## Quick start

```python
from loopiase import Loopia

client = Loopia("user@loopiaapi", "my_password")

# Check if a domain is available
if client.domain_is_free("example.com"):
    print("Available!")
```

## Guides

```{toctree}
:maxdepth: 2

usage/getting-started
usage/dns-management
usage/domain-registration
usage/billing
usage/reseller
```

## API Reference

```{toctree}
:maxdepth: 2

api/client
api/models
api/exceptions
```

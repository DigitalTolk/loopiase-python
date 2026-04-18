# Loopia Python Library

Python client library for the [Loopia](https://www.loopia.se) domain registrar API.

## Installation

```bash
pip install loopiase
```

## Usage

```python
from loopiase import Loopia, Record

client = Loopia("user@loopiaapi", "my_password")

# Check domain availability
if client.domain_is_free("example.com"):
    client.order_domain("example.com", has_accepted_terms=True)

# List domains
for domain in client.get_domains():
    print(domain.domain, domain.expiration_date)

# Manage DNS records
client.add_subdomain("example.com", "www")
client.add_zone_record("example.com", "www", Record(type="A", ttl=300, rdata="1.2.3.4"))

for record in client.get_zone_records("example.com", "www"):
    print(record.type, record.rdata)

# Billing
balance = client.get_credits_amount()
for invoice in client.get_unpaid_invoices():
    print(invoice.reference_no, invoice.to_pay, invoice.currency)
```

### Reseller

Reseller-specific methods are available under `client.reseller`:

```python
for customer in client.reseller.get_customers():
    print(customer.customer_number, customer.name)

# Operate on a customer's account
domains = client.get_domains(customer_number="C12345")
```

## Development

```bash
make install   # install with dev dependencies
make test      # run tests with coverage
make lint      # type-check with pyright
make docs      # build Sphinx documentation
```

## License

GPL-3.0

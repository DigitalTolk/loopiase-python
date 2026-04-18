# Domain registration

This guide covers checking availability, registering, transferring, and
managing domains.

## Check domain availability

```python
from loopiase import Loopia

client = Loopia("user@loopiaapi", "my_password")

if client.domain_is_free("my-new-site.com"):
    print("Domain is available!")
else:
    print("Domain is taken.")
```

## Register a domain

The account owner must accept the
[terms and conditions](https://www.loopia.com/terms-and-conditions/) before
registering.

```python
client.order_domain("my-new-site.com", has_accepted_terms=True)
```

## Add an existing domain

If you already own a domain and want to add it to your Loopia account
(without registering it):

```python
client.add_domain("my-existing-domain.com")
```

## Transfer a domain from another registrar

You will need the EPP/auth code from your current registrar.

```python
# 1. Add the domain to your Loopia account
client.add_domain("my-domain.com")

# 2. Initiate the transfer with the auth code
client.transfer_domain("my-domain.com", auth_code="X7k!mP2qR9")
```

```{note}
Some TLDs charge a fee for transfers. Check the Loopia price list.
```

## List your domains

```python
for domain in client.get_domains():
    status = "paid" if domain.paid else "unpaid"
    reg = "registered" if domain.registered else "pending"
    print(f"{domain.domain:30s}  {status:8s}  {reg:12s}  expires: {domain.expiration_date}")
```

Example output:

```text
example.com                     paid      registered    expires: 2025-12-31
another-site.se                 paid      registered    expires: 2026-03-15
```

## Get details for a single domain

```python
domain = client.get_domain("example.com")
print(f"Domain: {domain.domain}")
print(f"Paid: {domain.paid}")
print(f"Registered: {domain.registered}")
print(f"Renewal status: {domain.renewal_status}")
print(f"Expires: {domain.expiration_date}")
```

## Update nameservers

```python
client.update_dns_servers("example.com", [
    "ns1.loopia.se",
    "ns2.loopia.se",
])
```

At least two nameservers must be specified.

## Remove a domain

```python
client.remove_domain("old-domain.com")
```

```{warning}
This removes the domain from your Loopia account. It does not cancel the
registration — the domain remains registered until it expires.
```

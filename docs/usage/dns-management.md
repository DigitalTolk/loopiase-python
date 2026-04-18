# DNS management

This guide covers managing subdomains and DNS zone records.

## List subdomains

```python
from loopiase import Loopia

client = Loopia("user@loopiaapi", "my_password")

subdomains = client.get_subdomains("example.com")
print(subdomains)
# ['@', 'www', 'mail']
```

## Create a subdomain

```python
client.add_subdomain("example.com", "blog")
```

## Remove a subdomain

```python
client.remove_subdomain("example.com", "blog")
```

## Add a DNS record

Use the {class}`~loopiase.Record` dataclass to create records:

```python
from loopiase import Loopia, Record

client = Loopia("user@loopiaapi", "my_password")

# A record
a_record = Record(type="A", ttl=300, rdata="93.184.216.34")
client.add_zone_record("example.com", "www", a_record)

# MX record
mx_record = Record(type="MX", ttl=3600, priority=10, rdata="mail.example.com")
client.add_zone_record("example.com", "@", mx_record)

# CNAME record
cname = Record(type="CNAME", ttl=3600, rdata="www.example.com")
client.add_zone_record("example.com", "blog", cname)

# TXT record (e.g. SPF)
txt = Record(type="TXT", ttl=3600, rdata="v=spf1 include:_spf.example.com ~all")
client.add_zone_record("example.com", "@", txt)
```

## List DNS records

```python
records = client.get_zone_records("example.com", "@")
for r in records:
    print(f"{r.type:6s}  {r.rdata:40s}  TTL={r.ttl}  ID={r.record_id}")
```

Example output:

```text
A       93.184.216.34                             TTL=300   ID=12345
MX      mail.example.com                          TTL=3600  ID=12346
TXT     v=spf1 include:_spf.example.com ~all      TTL=3600  ID=12347
```

## Update a DNS record

To update a record you need its `record_id` (returned when listing records):

```python
# Fetch current records
records = client.get_zone_records("example.com", "www")

# Update the first A record's IP
for r in records:
    if r.type == "A":
        r.rdata = "198.51.100.42"
        r.ttl = 600
        client.update_zone_record("example.com", "www", r)
        break
```

## Delete a DNS record

```python
# Delete by record ID
client.remove_zone_record("example.com", "www", record_id=12345)
```

## Full example: set up a domain from scratch

```python
from loopiase import Loopia, Record

client = Loopia("user@loopiaapi", "my_password")
domain = "example.com"

# Create subdomains
client.add_subdomain(domain, "@")
client.add_subdomain(domain, "www")
client.add_subdomain(domain, "mail")

# Root A record
client.add_zone_record(domain, "@", Record(type="A", ttl=300, rdata="93.184.216.34"))

# www CNAME → root
client.add_zone_record(domain, "www", Record(type="CNAME", ttl=3600, rdata="example.com"))

# Mail
client.add_zone_record(domain, "@", Record(type="MX", ttl=3600, priority=10, rdata="mail.example.com"))
client.add_zone_record(domain, "mail", Record(type="A", ttl=3600, rdata="93.184.216.35"))

# SPF
client.add_zone_record(domain, "@", Record(
    type="TXT", ttl=3600, rdata="v=spf1 mx -all",
))

print(f"DNS setup complete for {domain}")
```

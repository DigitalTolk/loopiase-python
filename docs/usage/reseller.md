# Reseller operations

These methods are only available to Loopia reseller accounts.

## List your customers

```python
from loopiase import Loopia

client = Loopia("reseller@loopiaapi", "my_password")

for customer in client.reseller.get_customers():
    print(f"{customer.customer_number}  {customer.name:20s}  {customer.account_type}")
```

Example output:

```text
C10001  Jane Doe              HOSTING_BUSINESS
C10002  Acme Inc              LOOPIADOMAIN
C10003  Bob Smith             STARTER
```

## Manage a customer's account

Pass `customer_number` to any method to operate on a customer's account
instead of your own:

```python
# List a customer's domains
domains = client.get_domains(customer_number="C10001")
for d in domains:
    print(d.domain)

# Add a DNS record to a customer's domain
from loopiase import Record

record = Record(type="A", ttl=300, rdata="1.2.3.4")
client.add_zone_record("customer-site.com", "www", record, customer_number="C10001")

# Check a customer's unpaid invoices
invoices = client.get_unpaid_invoices(customer_number="C10001")
```

## Create a new customer account

```python
from loopiase import Loopia, Contact

client = Loopia("reseller@loopiaapi", "my_password")

owner = Contact(
    firstname="Jane",
    lastname="Doe",
    company="Doe Consulting",
    street="Main Street 1",
    zip="12345",
    city="Stockholm",
    country_iso2="se",
    orgno="556633-9304",
    phone="08-1234567",
    email="jane@doe-consulting.se",
)

result = client.reseller.create_new_account(
    "doe-consulting.se",
    owner,
    buy_domain=True,
    domain_configuration="PARKING",
    account_type="LOOPIADOMAIN",
)

print(f"Status: {result.status}")
print(f"Order reference: {result.order_reference}")
```

### Account types

| Value                   | Description                   |
|-------------------------|-------------------------------|
| `LOOPIADOMAIN`          | LoopiaDomain account          |
| `LOOPIADNS`             | LoopiaDNS account             |
| `EMAIL_PRIVATE`         | Email package                 |
| `STARTER`               | Starter package               |
| `HOSTING_PRIVATE`       | Web hosting Home              |
| `HOSTING_BUSINESS`      | Web hosting Business          |
| `HOSTING_BUSINESS_PLUS` | Web hosting Business Plus     |

### Domain configurations

| Value               | Description                    |
|---------------------|--------------------------------|
| `NO_CONFIG`         | No configuration               |
| `PARKING`           | Parked in LoopiaDNS            |
| `HOSTING_UNIX`      | Hosting configuration UNIX     |
| `HOSTING_AUTOBAHN`  | Hosting configuration Autobahn |
| `HOSTING_WINDOWS`   | Hosting configuration Windows  |

## Check order status

After creating an account, track the order:

```python
status = client.reseller.get_order_status("ORD-123456")
print(f"Status: {status.order_status}")
print(f"Customer number: {status.customer_number}")
```

| Order status | Meaning                                       |
|--------------|-----------------------------------------------|
| `DELETED`    | The order has been removed                    |
| `PENDING`    | The order is being processed                  |
| `PROCESSED`  | Account created, customer number is available |

## Transfer credits to a customer

```python
from loopiase import LoopiaError

try:
    client.reseller.transfer_credits_by_currency("C10001", 500.0, "SEK")
    print("Credits transferred!")
except LoopiaError as e:
    if e.status == "INSUFFICIENT_FUNDS":
        print("Not enough credits in your account.")
    else:
        raise
```

## Full example: provision a new customer

```python
from loopiase import Loopia, Contact, Record, LoopiaError

client = Loopia("reseller@loopiaapi", "my_password")

# 1. Create the account
owner = Contact(
    firstname="Bob", lastname="Smith",
    street="Oak Avenue 5", zip="54321", city="Gothenburg",
    country_iso2="se", email="bob@smith.se",
)

result = client.reseller.create_new_account(
    "bob-smith.se", owner,
    buy_domain=True,
    domain_configuration="PARKING",
    account_type="HOSTING_PRIVATE",
)
print(f"Order: {result.order_reference} → {result.status}")

# 2. Wait for processing, then check status
status = client.reseller.get_order_status(result.order_reference)
if status.order_status == "PROCESSED":
    cnum = status.customer_number
    print(f"Customer {cnum} created")

    # 3. Set up DNS
    client.add_subdomain("bob-smith.se", "www", customer_number=cnum)
    client.add_zone_record(
        "bob-smith.se", "www",
        Record(type="A", ttl=300, rdata="93.184.216.34"),
        customer_number=cnum,
    )

    # 4. Transfer some credits
    client.reseller.transfer_credits_by_currency(cnum, 200.0, "SEK")
    print("Provisioning complete!")
```

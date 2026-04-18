# Billing and credits

This guide covers invoices and LoopiaPREPAID credits.

## Check your credit balance

```python
from loopiase import Loopia

client = Loopia("user@loopiaapi", "my_password")

balance = client.get_credits_amount()
print(f"Balance: {balance:.2f} SEK")
```

## List unpaid invoices

```python
invoices = client.get_unpaid_invoices()

if not invoices:
    print("No unpaid invoices!")
else:
    for inv in invoices:
        print(f"Invoice {inv.reference_no}: {inv.to_pay:.2f} {inv.currency} (due: {inv.expires})")
```

Example output:

```text
Invoice INV-12345: 125.00 SEK (due: 2025-06-01)
Invoice INV-12346: 89.00 SEK (due: 2025-06-15)
```

## Get invoice details

```python
invoice = client.get_invoice("INV-12345")
print(f"Invoice: {invoice.reference_no}")
print(f"Total: {invoice.total:.2f} {invoice.currency}")
print(f"VAT: {invoice.vat:.2f}")
print(f"Credits applied: {invoice.credits:.2f}")
print(f"To pay: {invoice.to_pay:.2f}")
print(f"Due date: {invoice.expires}")
print()
print("Line items:")
for item in invoice.items:
    print(f"  {item.product:30s}  {item.subtotal:>8.2f} {invoice.currency}")
```

## Pay an invoice using credits

```python
from loopiase import LoopiaError

try:
    client.pay_invoice_using_credits("INV-12345")
    print("Invoice paid!")
except LoopiaError as e:
    if e.status == "INSUFFICIENT_FUNDS":
        print("Not enough credits to pay this invoice.")
    else:
        raise
```

## Full example: auto-pay all unpaid invoices

```python
from loopiase import Loopia, LoopiaError

client = Loopia("user@loopiaapi", "my_password")

balance = client.get_credits_amount()
print(f"Current balance: {balance:.2f} SEK")

for invoice in client.get_unpaid_invoices():
    if invoice.to_pay <= balance:
        try:
            client.pay_invoice_using_credits(invoice.reference_no)
            balance -= invoice.to_pay
            print(f"Paid {invoice.reference_no} ({invoice.to_pay:.2f} {invoice.currency})")
        except LoopiaError as e:
            print(f"Failed to pay {invoice.reference_no}: {e.status}")
    else:
        print(f"Skipping {invoice.reference_no}: {invoice.to_pay:.2f} exceeds balance {balance:.2f}")
```

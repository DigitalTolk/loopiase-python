# Getting started

## Create an API user

Before using this library you need to create an API user in the
[Loopia Customer Zone](https://www.loopia.com/login/) under
**Account Settings** → **LoopiaAPI**.

## Initialize the client

```python
from loopiase import Loopia

client = Loopia("user@loopiaapi", "my_password")
```

You can point to a different endpoint (useful for testing):

```python
client = Loopia("user@loopiaapi", "my_password", url="https://api.loopia.test/RPCSERV")
```

## Rate limits

Loopia allows up to **60 calls per minute**. Of those, a maximum of 15 can be
domain searches. Resellers can make a maximum of 15 domain registrations per
hour by direct activation.

## Error handling

Methods that modify state return `"OK"` on success. On failure they raise
{class}`~loopiase.LoopiaError` with a `status` attribute:

```python
from loopiase import Loopia, LoopiaError

client = Loopia("user@loopiaapi", "my_password")

try:
    client.add_domain("example.com")
except LoopiaError as e:
    match e.status:
        case "AUTH_ERROR":
            print("Invalid credentials")
        case "BAD_INDATA":
            print("Invalid domain name")
        case "RATE_LIMITED":
            print("Too many requests, slow down")
        case _:
            print(f"API error: {e.status}")
```

Possible status values:

| Status                | Meaning                                          |
|-----------------------|--------------------------------------------------|
| `OK`                  | Success (never raised as an error)               |
| `AUTH_ERROR`          | Wrong username or password                       |
| `DOMAIN_OCCUPIED`     | Domain is not available for registration         |
| `RATE_LIMITED`        | Too many API calls                               |
| `BAD_INDATA`         | A parameter has an invalid value                 |
| `UNKNOWN_ERROR`       | Something went wrong                             |
| `INSUFFICIENT_FUNDS`  | Not enough credits for the operation             |

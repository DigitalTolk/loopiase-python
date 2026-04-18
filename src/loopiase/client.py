from __future__ import annotations

import xmlrpc.client
from typing import Any, cast

from loopiase.exceptions import LoopiaError
from loopiase.models import (
    Contact,
    CreateAccountStatus,
    Customer,
    Domain,
    Invoice,
    OrderStatus,
    Record,
)

API_URL = "https://api.loopia.se/RPCSERV"


def _call(client: xmlrpc.client.ServerProxy, method: str, *args: Any) -> Any:
    """Call an XML-RPC method and return the result as Any."""
    return cast(Any, getattr(client, method)(*args))


def _check_status(result: Any) -> str:
    if isinstance(result, str):
        status = result
    elif isinstance(result, list) and len(result) == 1 and isinstance(result[0], str):
        status = result[0]
    else:
        return result  # type: ignore[return-value]
    if status != "OK":
        raise LoopiaError(status)
    return status


class Reseller:
    """Reseller-only API methods.

    Accessed via :attr:`Loopia.reseller`::

        client = Loopia("reseller@loopiaapi", "password")
        customers = client.reseller.get_customers()
    """

    def __init__(self, loopia: Loopia) -> None:
        self._loopia = loopia

    def get_customers(self) -> list[Customer]:
        """List all sub-customers.

        Example::

            for customer in client.reseller.get_customers():
                print(customer.customer_number, customer.name)
        """
        result: list[dict[str, Any]] = self._loopia._call(
            "getCustomers", self._loopia._username, self._loopia._password,
        )
        return [Customer.from_dict(c) for c in result]

    def get_order_status(
        self,
        order_reference: str,
        *,
        customer_number: str | None = None,
    ) -> OrderStatus:
        """Check the status of an order created by :meth:`create_new_account`.

        Possible statuses: ``DELETED``, ``PENDING``, ``PROCESSED``.
        """
        result: dict[str, Any] = self._loopia._call(
            "getOrderStatus",
            *self._loopia._auth(customer_number),
            order_reference,
        )
        return OrderStatus.from_dict(result)

    def create_new_account(
        self,
        domain: str,
        owner_contact: Contact,
        *,
        billing_contact_reseller: bool = False,
        tech_contact_reseller: bool = False,
        buy_domain: bool = False,
        domain_configuration: str = "NO_CONFIG",
        account_type: str = "LOOPIADOMAIN",
        end_user_has_accepted_terms: bool = True,
    ) -> CreateAccountStatus:
        """Create a new Loopia customer account.

        Example::

            from loopia import Contact

            owner = Contact(
                firstname="Jane",
                lastname="Doe",
                email="jane@example.com",
                street="Main St 1",
                zip="12345",
                city="Stockholm",
                country_iso2="se",
            )
            result = client.reseller.create_new_account(
                "newcustomer.com",
                owner,
                buy_domain=True,
                domain_configuration="PARKING",
                account_type="LOOPIADOMAIN",
            )
            print(result.status, result.order_reference)
        """
        result: dict[str, Any] = self._loopia._call(
            "createNewAccount",
            self._loopia._username,
            self._loopia._password,
            domain,
            owner_contact.to_dict(),
            billing_contact_reseller,
            tech_contact_reseller,
            buy_domain,
            domain_configuration,
            account_type,
            end_user_has_accepted_terms,
        )
        return CreateAccountStatus.from_dict(result)

    def transfer_credits_by_currency(
        self,
        customer_id: str,
        amount: float,
        currency: str,
    ) -> str:
        """Transfer LoopiaPREPAID credits to a sub-customer.

        Example::

            client.reseller.transfer_credits_by_currency("C12345", 100.0, "SEK")
        """
        result = self._loopia._call(
            "transferCreditsByCurrency",
            self._loopia._username,
            self._loopia._password,
            customer_id,
            amount,
            currency,
        )
        return _check_status(result)


class Loopia:
    """Client for the Loopia XML-RPC API.

    Example::

        from loopia import Loopia

        client = Loopia("user@loopiaapi", "my_password")
        domains = client.get_domains()
    """

    def __init__(
        self,
        username: str,
        password: str,
        *,
        url: str = API_URL,
    ) -> None:
        self._username = username
        self._password = password
        self._client = xmlrpc.client.ServerProxy(url, encoding="utf-8")
        self.reseller = Reseller(self)
        """Reseller-only methods. See :class:`Reseller`."""

    def _call(self, method: str, *args: Any) -> Any:
        return _call(self._client, method, *args)

    def _auth(self, customer_number: str | None) -> list[str]:
        args: list[str] = [self._username, self._password]
        if customer_number is not None:
            args.append(customer_number)
        return args

    # ── Domain methods ──────────────────────────────────────────

    def add_domain(
        self,
        domain: str,
        *,
        customer_number: str | None = None,
    ) -> str:
        """Add an existing domain to a Loopia account.

        Example::

            client.add_domain("example.com")
        """
        result = self._call("addDomain", *self._auth(customer_number), domain)
        return _check_status(result)

    def remove_domain(
        self,
        domain: str,
        *,
        customer_number: str | None = None,
    ) -> str:
        """Remove a domain from a Loopia account."""
        result = self._call("removeDomain", *self._auth(customer_number), domain)
        return _check_status(result)

    def get_domain(
        self,
        domain: str,
        *,
        customer_number: str | None = None,
    ) -> Domain:
        """Get information about a specific domain.

        Example::

            domain = client.get_domain("example.com")
            print(domain.expiration_date, domain.paid)
        """
        result = self._call("getDomain", *self._auth(customer_number), domain)
        if isinstance(result, list) and result:
            return Domain.from_dict(result[0])
        return Domain.from_dict(cast(dict[str, Any], result))

    def get_domains(
        self,
        *,
        customer_number: str | None = None,
    ) -> list[Domain]:
        """List all domains on the account.

        Example::

            for domain in client.get_domains():
                print(domain.domain, domain.expiration_date)
        """
        result: list[dict[str, Any]] = self._call(
            "getDomains", *self._auth(customer_number),
        )
        return [Domain.from_dict(d) for d in result]

    def domain_is_free(self, domain: str) -> bool:
        """Check whether a domain is available for registration.

        Returns ``True`` if the domain is free, ``False`` if occupied.

        Example::

            if client.domain_is_free("example.com"):
                print("Available!")
        """
        result = self._call("domainIsFree", self._username, self._password, domain)
        status = result if isinstance(result, str) else result[0] if isinstance(result, list) else result
        return status == "OK"

    def order_domain(
        self,
        domain: str,
        has_accepted_terms: bool,
        *,
        customer_number: str | None = None,
    ) -> str:
        """Register a new domain.

        The account owner must have accepted the terms and conditions at
        loopia.com/terms-and-conditions/ before calling this method.

        Example::

            client.order_domain("example.com", has_accepted_terms=True)
        """
        result = self._call(
            "orderDomain",
            *self._auth(customer_number),
            domain,
            has_accepted_terms,
        )
        return _check_status(result)

    def transfer_domain(
        self,
        domain: str,
        auth_code: str,
        *,
        customer_number: str | None = None,
    ) -> str:
        """Transfer a domain to Loopia from another registrar.

        Example::

            client.transfer_domain("example.com", auth_code="EPP-AUTH-CODE")
        """
        result = self._call(
            "transferDomain",
            *self._auth(customer_number),
            domain,
            auth_code,
        )
        return _check_status(result)

    def update_dns_servers(
        self,
        domain: str,
        nameservers: list[str],
        *,
        customer_number: str | None = None,
    ) -> str:
        """Update the nameservers for a domain. At least two must be specified.

        Example::

            client.update_dns_servers("example.com", ["ns1.loopia.se", "ns2.loopia.se"])
        """
        result = self._call(
            "updateDNSServers",
            *self._auth(customer_number),
            domain,
            nameservers,
        )
        return _check_status(result)

    # ── Subdomain methods ───────────────────────────────────────

    def add_subdomain(
        self,
        domain: str,
        subdomain: str,
        *,
        customer_number: str | None = None,
    ) -> str:
        """Create a subdomain under a domain.

        Example::

            client.add_subdomain("example.com", "www")
        """
        result = self._call(
            "addSubdomain",
            *self._auth(customer_number),
            domain,
            subdomain,
        )
        return _check_status(result)

    def remove_subdomain(
        self,
        domain: str,
        subdomain: str,
        *,
        customer_number: str | None = None,
    ) -> str:
        """Remove a subdomain."""
        result = self._call(
            "removeSubdomain",
            *self._auth(customer_number),
            domain,
            subdomain,
        )
        return _check_status(result)

    def get_subdomains(
        self,
        domain: str,
        *,
        customer_number: str | None = None,
    ) -> list[str]:
        """List all subdomains for a domain.

        Example::

            subdomains = client.get_subdomains("example.com")
            # ['@', 'www', 'mail']
        """
        result: list[str] = self._call(
            "getSubdomains", *self._auth(customer_number), domain,
        )
        return result

    # ── Zone record methods ─────────────────────────────────────

    def add_zone_record(
        self,
        domain: str,
        subdomain: str,
        record: Record,
        *,
        customer_number: str | None = None,
    ) -> str:
        """Add a DNS record to a subdomain.

        Example::

            from loopia import Record

            record = Record(type="A", ttl=300, rdata="93.184.216.34")
            client.add_zone_record("example.com", "@", record)
        """
        result = self._call(
            "addZoneRecord",
            *self._auth(customer_number),
            domain,
            subdomain,
            record.to_dict(),
        )
        return _check_status(result)

    def get_zone_records(
        self,
        domain: str,
        subdomain: str,
        *,
        customer_number: str | None = None,
    ) -> list[Record]:
        """Get all DNS records for a subdomain.

        Example::

            for record in client.get_zone_records("example.com", "@"):
                print(record.type, record.rdata, record.ttl)
        """
        result: list[dict[str, Any]] = self._call(
            "getZoneRecords",
            *self._auth(customer_number),
            domain,
            subdomain,
        )
        return [Record.from_dict(r) for r in result]

    def update_zone_record(
        self,
        domain: str,
        subdomain: str,
        record: Record,
        *,
        customer_number: str | None = None,
    ) -> str:
        """Update an existing DNS record. The ``record.record_id`` must be set.

        Example::

            record = Record(type="A", ttl=600, rdata="1.2.3.4", record_id=42)
            client.update_zone_record("example.com", "@", record)
        """
        result = self._call(
            "updateZoneRecord",
            *self._auth(customer_number),
            domain,
            subdomain,
            record.to_dict(),
        )
        return _check_status(result)

    def remove_zone_record(
        self,
        domain: str,
        subdomain: str,
        record_id: int,
        *,
        customer_number: str | None = None,
    ) -> str:
        """Delete a DNS record by its ID.

        Example::

            client.remove_zone_record("example.com", "@", record_id=42)
        """
        result = self._call(
            "removeZoneRecord",
            *self._auth(customer_number),
            domain,
            subdomain,
            record_id,
        )
        return _check_status(result)

    # ── Invoice / credits methods ───────────────────────────────

    def get_invoice(
        self,
        invoice_number: str,
        *,
        customer_number: str | None = None,
    ) -> Invoice:
        """Retrieve a specific invoice by its reference number.

        Example::

            invoice = client.get_invoice("INV-12345")
            print(invoice.to_pay, invoice.currency)
            for item in invoice.items:
                print(item.product, item.subtotal)
        """
        result: dict[str, Any] = self._call(
            "getInvoice",
            *self._auth(customer_number),
            invoice_number,
        )
        return Invoice.from_dict(result)

    def get_unpaid_invoices(
        self,
        *,
        customer_number: str | None = None,
    ) -> list[Invoice]:
        """List all unpaid invoices on the account.

        Example::

            for invoice in client.get_unpaid_invoices():
                print(invoice.reference_no, invoice.to_pay, invoice.currency)
        """
        result: list[dict[str, Any]] = self._call(
            "getUnpaidInvoices", *self._auth(customer_number),
        )
        return [Invoice.from_dict(i) for i in result]

    def pay_invoice_using_credits(
        self,
        invoice_number: str,
        *,
        customer_number: str | None = None,
    ) -> str:
        """Pay an invoice using LoopiaPREPAID credits.

        Raises :class:`~loopia.LoopiaError` with status ``INSUFFICIENT_FUNDS``
        if the balance is too low.
        """
        result = self._call(
            "payInvoiceUsingCredits",
            *self._auth(customer_number),
            invoice_number,
        )
        return _check_status(result)

    def get_credits_amount(
        self,
        *,
        customer_number: str | None = None,
        with_vat: bool = False,
    ) -> float:
        """Get the current LoopiaPREPAID balance.

        Example::

            balance = client.get_credits_amount()
            print(f"Balance: {balance} SEK")
        """
        args: list[Any] = list(self._auth(customer_number))
        args.append(with_vat)
        result: float = self._call("getCreditsAmount", *args)
        return float(result)

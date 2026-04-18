from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Record:
    """DNS zone record."""

    type: str = ""
    ttl: int = 3600
    priority: int = 0
    rdata: str = ""
    record_id: int = 0

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "ttl": self.ttl,
            "priority": self.priority,
            "rdata": self.rdata,
            "record_id": self.record_id,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Record:
        return cls(
            type=data.get("type", ""),
            ttl=data.get("ttl", 3600),
            priority=data.get("priority", 0),
            rdata=data.get("rdata", ""),
            record_id=data.get("record_id", 0),
        )


@dataclass
class Domain:
    """Domain name information."""

    domain: str = ""
    paid: bool = False
    registered: bool = False
    renewal_status: str = ""
    expiration_date: str = ""
    reference_no: int = 0

    @classmethod
    def from_dict(cls, data: dict) -> Domain:
        return cls(
            domain=data.get("domain", ""),
            paid=bool(data.get("paid", 0)),
            registered=bool(data.get("registered", 0)),
            renewal_status=data.get("renewal_status", ""),
            expiration_date=data.get("expiration_date", ""),
            reference_no=data.get("reference_no", 0),
        )


@dataclass
class Customer:
    """Customer account information."""

    company: str = ""
    name: str = ""
    customer_number: str = ""
    account_type: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> Customer:
        return cls(
            company=data.get("company", ""),
            name=data.get("name", ""),
            customer_number=data.get("customer_number", ""),
            account_type=data.get("account_type", ""),
        )


@dataclass
class InvoiceItem:
    """Invoice line item."""

    product: str = ""
    until: str = ""
    fee: float = 0.0
    discount: float = 0.0
    items: float = 0.0
    subtotal: float = 0.0

    @classmethod
    def from_dict(cls, data: dict) -> InvoiceItem:
        return cls(
            product=data.get("product", ""),
            until=data.get("until", ""),
            fee=float(data.get("fee", 0)),
            discount=float(data.get("discount", 0)),
            items=float(data.get("items", 0)),
            subtotal=float(data.get("subtotal", 0)),
        )


@dataclass
class Invoice:
    """Invoice information."""

    reference_no: str = ""
    total: float = 0.0
    credits: float = 0.0
    vat: float = 0.0
    to_pay: float = 0.0
    currency: str = ""
    expires: str = ""
    items: list[InvoiceItem] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> Invoice:
        items_data = data.get("items", [])
        return cls(
            reference_no=data.get("reference_no", ""),
            total=float(data.get("total", 0)),
            credits=float(data.get("credits", 0)),
            vat=float(data.get("vat", 0)),
            to_pay=float(data.get("to_pay", 0)),
            currency=data.get("currency", ""),
            expires=data.get("expires", ""),
            items=[InvoiceItem.from_dict(i) for i in items_data],
        )


@dataclass
class OrderStatus:
    """Order status information."""

    order_status: str = ""
    customer_number: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> OrderStatus:
        return cls(
            order_status=data.get("order_status", ""),
            customer_number=data.get("customer_number", ""),
        )


@dataclass
class CreateAccountStatus:
    """Account creation result."""

    status: str = ""
    order_reference: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> CreateAccountStatus:
        return cls(
            status=data.get("status", ""),
            order_reference=data.get("order_reference", ""),
        )


@dataclass
class Contact:
    """Contact information for domain registration."""

    firstname: str = ""
    lastname: str = ""
    company: str = ""
    street: str = ""
    street2: str = ""
    zip: str = ""
    city: str = ""
    country_iso2: str = ""
    orgno: str = ""
    norid_pid: str = ""
    phone: str = ""
    cell: str = ""
    fax: str = ""
    email: str = ""

    def to_dict(self) -> dict:
        return {
            "firstname": self.firstname,
            "lastname": self.lastname,
            "company": self.company,
            "street": self.street,
            "street2": self.street2,
            "zip": self.zip,
            "city": self.city,
            "country_iso2": self.country_iso2,
            "orgno": self.orgno,
            "norid_pid": self.norid_pid,
            "phone": self.phone,
            "cell": self.cell,
            "fax": self.fax,
            "email": self.email,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Contact:
        return cls(**{k: data.get(k, "") for k in cls.__dataclass_fields__})

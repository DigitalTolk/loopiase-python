import unittest

from loopiase.models import (
    Contact,
    CreateAccountStatus,
    Customer,
    Domain,
    Invoice,
    InvoiceItem,
    OrderStatus,
    Record,
)


class TestRecord(unittest.TestCase):
    def test_defaults(self):
        r = Record()
        self.assertEqual(r.type, "")
        self.assertEqual(r.ttl, 3600)
        self.assertEqual(r.priority, 0)
        self.assertEqual(r.rdata, "")
        self.assertEqual(r.record_id, 0)

    def test_to_dict(self):
        r = Record(type="A", ttl=300, priority=0, rdata="127.0.0.1", record_id=1)
        d = r.to_dict()
        self.assertEqual(d["type"], "A")
        self.assertEqual(d["ttl"], 300)
        self.assertEqual(d["rdata"], "127.0.0.1")
        self.assertEqual(d["record_id"], 1)

    def test_from_dict(self):
        r = Record.from_dict({"type": "MX", "ttl": 600, "priority": 10, "rdata": "mail.example.com", "record_id": 42})
        self.assertEqual(r.type, "MX")
        self.assertEqual(r.ttl, 600)
        self.assertEqual(r.priority, 10)
        self.assertEqual(r.rdata, "mail.example.com")
        self.assertEqual(r.record_id, 42)

    def test_from_dict_missing_fields(self):
        r = Record.from_dict({})
        self.assertEqual(r.type, "")
        self.assertEqual(r.ttl, 3600)

    def test_roundtrip(self):
        r = Record(type="CNAME", ttl=900, priority=0, rdata="alias.example.com", record_id=5)
        r2 = Record.from_dict(r.to_dict())
        self.assertEqual(r, r2)


class TestDomain(unittest.TestCase):
    def test_from_dict(self):
        d = Domain.from_dict({
            "domain": "example.com",
            "paid": 1,
            "registered": 1,
            "renewal_status": "ACTIVE",
            "expiration_date": "2025-01-01",
            "reference_no": 12345,
        })
        self.assertEqual(d.domain, "example.com")
        self.assertTrue(d.paid)
        self.assertTrue(d.registered)
        self.assertEqual(d.renewal_status, "ACTIVE")
        self.assertEqual(d.expiration_date, "2025-01-01")
        self.assertEqual(d.reference_no, 12345)

    def test_from_dict_unpaid(self):
        d = Domain.from_dict({"domain": "test.com", "paid": 0, "registered": 0})
        self.assertFalse(d.paid)
        self.assertFalse(d.registered)

    def test_from_dict_missing_fields(self):
        d = Domain.from_dict({})
        self.assertEqual(d.domain, "")
        self.assertFalse(d.paid)


class TestCustomer(unittest.TestCase):
    def test_from_dict(self):
        c = Customer.from_dict({
            "company": "Acme Inc",
            "name": "John Doe",
            "customer_number": "C123",
            "account_type": "HOSTING_BUSINESS",
        })
        self.assertEqual(c.company, "Acme Inc")
        self.assertEqual(c.name, "John Doe")
        self.assertEqual(c.customer_number, "C123")
        self.assertEqual(c.account_type, "HOSTING_BUSINESS")

    def test_from_dict_missing_fields(self):
        c = Customer.from_dict({})
        self.assertEqual(c.company, "")
        self.assertEqual(c.name, "")


class TestInvoiceItem(unittest.TestCase):
    def test_from_dict(self):
        item = InvoiceItem.from_dict({
            "product": "Domain .com",
            "until": "2025-12-31",
            "fee": 99.0,
            "discount": 10.0,
            "items": 1.0,
            "subtotal": 89.0,
        })
        self.assertEqual(item.product, "Domain .com")
        self.assertEqual(item.fee, 99.0)
        self.assertEqual(item.discount, 10.0)
        self.assertEqual(item.subtotal, 89.0)


class TestInvoice(unittest.TestCase):
    def test_from_dict(self):
        inv = Invoice.from_dict({
            "reference_no": "INV-001",
            "total": 100.0,
            "credits": 10.0,
            "vat": 25.0,
            "to_pay": 115.0,
            "currency": "SEK",
            "expires": "2025-06-01",
            "items": [
                {"product": "Hosting", "until": "", "fee": 80.0, "discount": 0.0, "items": 1.0, "subtotal": 80.0},
                {"product": "Domain", "until": "", "fee": 20.0, "discount": 0.0, "items": 1.0, "subtotal": 20.0},
            ],
        })
        self.assertEqual(inv.reference_no, "INV-001")
        self.assertEqual(inv.total, 100.0)
        self.assertEqual(inv.currency, "SEK")
        self.assertEqual(len(inv.items), 2)
        self.assertEqual(inv.items[0].product, "Hosting")
        self.assertEqual(inv.items[1].product, "Domain")

    def test_from_dict_no_items(self):
        inv = Invoice.from_dict({"reference_no": "INV-002"})
        self.assertEqual(inv.items, [])


class TestOrderStatus(unittest.TestCase):
    def test_from_dict(self):
        os = OrderStatus.from_dict({
            "order_status": "PROCESSED",
            "customer_number": "C999",
        })
        self.assertEqual(os.order_status, "PROCESSED")
        self.assertEqual(os.customer_number, "C999")


class TestCreateAccountStatus(unittest.TestCase):
    def test_from_dict(self):
        cas = CreateAccountStatus.from_dict({
            "status": "OK",
            "order_reference": "REF-123",
        })
        self.assertEqual(cas.status, "OK")
        self.assertEqual(cas.order_reference, "REF-123")


class TestContact(unittest.TestCase):
    def test_to_dict(self):
        c = Contact(
            firstname="Jane",
            lastname="Doe",
            company="Acme",
            street="Main St 1",
            street2="",
            zip="12345",
            city="Stockholm",
            country_iso2="se",
            orgno="556633-9304",
            norid_pid="",
            phone="021-128222",
            cell="",
            fax="",
            email="jane@example.com",
        )
        d = c.to_dict()
        self.assertEqual(d["firstname"], "Jane")
        self.assertEqual(d["lastname"], "Doe")
        self.assertEqual(d["country_iso2"], "se")
        self.assertEqual(d["email"], "jane@example.com")

    def test_from_dict(self):
        c = Contact.from_dict({"firstname": "John", "lastname": "Smith", "email": "john@example.com"})
        self.assertEqual(c.firstname, "John")
        self.assertEqual(c.lastname, "Smith")
        self.assertEqual(c.email, "john@example.com")
        self.assertEqual(c.company, "")

    def test_roundtrip(self):
        c = Contact(firstname="A", lastname="B", email="a@b.com")
        c2 = Contact.from_dict(c.to_dict())
        self.assertEqual(c, c2)


if __name__ == "__main__":
    unittest.main()

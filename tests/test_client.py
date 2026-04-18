import unittest
from unittest.mock import MagicMock, patch

from loopiase.client import Loopia, _check_status
from loopiase.exceptions import LoopiaError
from loopiase.models import Contact, Record


class LoopiaTestCase(unittest.TestCase):
    """Base class that patches the XML-RPC ServerProxy."""

    def setUp(self):
        patcher = patch("loopiase.client.xmlrpc.client.ServerProxy")
        self.mock_proxy_cls = patcher.start()
        self.addCleanup(patcher.stop)
        self.mock_rpc = MagicMock()
        self.mock_proxy_cls.return_value = self.mock_rpc
        self.client = Loopia("user@loopiaapi", "secret")


class TestInit(LoopiaTestCase):
    def test_creates_proxy_with_default_url(self):
        self.mock_proxy_cls.assert_called_once_with(
            "https://api.loopia.se/RPCSERV",
            encoding="utf-8",
        )

    def test_creates_proxy_with_custom_url(self):
        self.mock_proxy_cls.reset_mock()
        Loopia("u", "p", url="https://custom.example.com/RPC")
        self.mock_proxy_cls.assert_called_once_with(
            "https://custom.example.com/RPC",
            encoding="utf-8",
        )

    def test_reseller_attribute(self):
        self.assertIsNotNone(self.client.reseller)


class TestCheckStatus(unittest.TestCase):
    def test_ok_string(self):
        self.assertEqual(_check_status("OK"), "OK")

    def test_ok_list(self):
        self.assertEqual(_check_status(["OK"]), "OK")

    def test_error_string(self):
        with self.assertRaises(LoopiaError) as ctx:
            _check_status("AUTH_ERROR")
        self.assertEqual(ctx.exception.status, "AUTH_ERROR")

    def test_error_list(self):
        with self.assertRaises(LoopiaError) as ctx:
            _check_status(["BAD_INDATA"])
        self.assertEqual(ctx.exception.status, "BAD_INDATA")

    def test_passthrough_dict(self):
        data = {"key": "value"}
        self.assertEqual(_check_status(data), data)

    def test_passthrough_list_of_dicts(self):
        data = [{"a": 1}, {"b": 2}]
        self.assertEqual(_check_status(data), data)


# ── Domain methods ──────────────────────────────────────────────


class TestAddDomain(LoopiaTestCase):
    def test_success(self):
        self.mock_rpc.addDomain.return_value = "OK"
        result = self.client.add_domain("example.com")
        self.assertEqual(result, "OK")
        self.mock_rpc.addDomain.assert_called_once_with("user@loopiaapi", "secret", "example.com")

    def test_with_customer_number(self):
        self.mock_rpc.addDomain.return_value = "OK"
        result = self.client.add_domain("example.com", customer_number="C123")
        self.assertEqual(result, "OK")
        self.mock_rpc.addDomain.assert_called_once_with("user@loopiaapi", "secret", "C123", "example.com")

    def test_error(self):
        self.mock_rpc.addDomain.return_value = "AUTH_ERROR"
        with self.assertRaises(LoopiaError):
            self.client.add_domain("example.com")


class TestRemoveDomain(LoopiaTestCase):
    def test_success(self):
        self.mock_rpc.removeDomain.return_value = "OK"
        result = self.client.remove_domain("example.com")
        self.assertEqual(result, "OK")
        self.mock_rpc.removeDomain.assert_called_once_with("user@loopiaapi", "secret", "example.com")


class TestGetDomain(LoopiaTestCase):
    def test_returns_domain_from_list(self):
        self.mock_rpc.getDomain.return_value = [{
            "domain": "example.com",
            "paid": 1,
            "registered": 1,
            "renewal_status": "ACTIVE",
            "expiration_date": "2025-01-01",
            "reference_no": 0,
        }]
        domain = self.client.get_domain("example.com")
        self.assertEqual(domain.domain, "example.com")
        self.assertTrue(domain.paid)
        self.assertTrue(domain.registered)

    def test_returns_domain_from_dict(self):
        self.mock_rpc.getDomain.return_value = {
            "domain": "test.se",
            "paid": 0,
            "registered": 0,
        }
        domain = self.client.get_domain("test.se")
        self.assertEqual(domain.domain, "test.se")
        self.assertFalse(domain.paid)


class TestGetDomains(LoopiaTestCase):
    def test_returns_list(self):
        self.mock_rpc.getDomains.return_value = [
            {"domain": "a.com", "paid": 1, "registered": 1},
            {"domain": "b.com", "paid": 0, "registered": 0},
        ]
        domains = self.client.get_domains()
        self.assertEqual(len(domains), 2)
        self.assertEqual(domains[0].domain, "a.com")
        self.assertEqual(domains[1].domain, "b.com")

    def test_empty(self):
        self.mock_rpc.getDomains.return_value = []
        domains = self.client.get_domains()
        self.assertEqual(domains, [])


class TestDomainIsFree(LoopiaTestCase):
    def test_free(self):
        self.mock_rpc.domainIsFree.return_value = "OK"
        self.assertTrue(self.client.domain_is_free("available.com"))

    def test_occupied(self):
        self.mock_rpc.domainIsFree.return_value = "DOMAIN_OCCUPIED"
        self.assertFalse(self.client.domain_is_free("taken.com"))


class TestOrderDomain(LoopiaTestCase):
    def test_success(self):
        self.mock_rpc.orderDomain.return_value = "OK"
        result = self.client.order_domain("example.com", True)
        self.assertEqual(result, "OK")
        self.mock_rpc.orderDomain.assert_called_once_with(
            "user@loopiaapi", "secret", "example.com", True,
        )


class TestTransferDomain(LoopiaTestCase):
    def test_success(self):
        self.mock_rpc.transferDomain.return_value = "OK"
        result = self.client.transfer_domain("example.com", "AUTH123")
        self.assertEqual(result, "OK")
        self.mock_rpc.transferDomain.assert_called_once_with(
            "user@loopiaapi", "secret", "example.com", "AUTH123",
        )


class TestUpdateDNSServers(LoopiaTestCase):
    def test_success(self):
        self.mock_rpc.updateDNSServers.return_value = "OK"
        ns = ["ns1.loopia.se", "ns2.loopia.se"]
        result = self.client.update_dns_servers("example.com", ns)
        self.assertEqual(result, "OK")
        self.mock_rpc.updateDNSServers.assert_called_once_with(
            "user@loopiaapi", "secret", "example.com", ns,
        )


# ── Subdomain methods ──────────────────────────────────────────


class TestAddSubdomain(LoopiaTestCase):
    def test_success(self):
        self.mock_rpc.addSubdomain.return_value = "OK"
        result = self.client.add_subdomain("example.com", "www")
        self.assertEqual(result, "OK")
        self.mock_rpc.addSubdomain.assert_called_once_with(
            "user@loopiaapi", "secret", "example.com", "www",
        )


class TestRemoveSubdomain(LoopiaTestCase):
    def test_success(self):
        self.mock_rpc.removeSubdomain.return_value = "OK"
        result = self.client.remove_subdomain("example.com", "www")
        self.assertEqual(result, "OK")


class TestGetSubdomains(LoopiaTestCase):
    def test_returns_list(self):
        self.mock_rpc.getSubdomains.return_value = ["@", "www", "mail"]
        subs = self.client.get_subdomains("example.com")
        self.assertEqual(subs, ["@", "www", "mail"])


# ── Zone record methods ────────────────────────────────────────


class TestAddZoneRecord(LoopiaTestCase):
    def test_success(self):
        self.mock_rpc.addZoneRecord.return_value = "OK"
        record = Record(type="A", ttl=300, rdata="1.2.3.4")
        result = self.client.add_zone_record("example.com", "@", record)
        self.assertEqual(result, "OK")
        self.mock_rpc.addZoneRecord.assert_called_once_with(
            "user@loopiaapi", "secret", "example.com", "@", record.to_dict(),
        )


class TestGetZoneRecords(LoopiaTestCase):
    def test_returns_records(self):
        self.mock_rpc.getZoneRecords.return_value = [
            {"type": "A", "ttl": 3600, "priority": 0, "rdata": "1.2.3.4", "record_id": 1},
            {"type": "MX", "ttl": 3600, "priority": 10, "rdata": "mail.example.com", "record_id": 2},
        ]
        records = self.client.get_zone_records("example.com", "@")
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0].type, "A")
        self.assertEqual(records[1].type, "MX")
        self.assertEqual(records[1].priority, 10)


class TestUpdateZoneRecord(LoopiaTestCase):
    def test_success(self):
        self.mock_rpc.updateZoneRecord.return_value = "OK"
        record = Record(type="A", ttl=300, rdata="5.6.7.8", record_id=1)
        result = self.client.update_zone_record("example.com", "@", record)
        self.assertEqual(result, "OK")


class TestRemoveZoneRecord(LoopiaTestCase):
    def test_success(self):
        self.mock_rpc.removeZoneRecord.return_value = "OK"
        result = self.client.remove_zone_record("example.com", "@", 42)
        self.assertEqual(result, "OK")
        self.mock_rpc.removeZoneRecord.assert_called_once_with(
            "user@loopiaapi", "secret", "example.com", "@", 42,
        )


# ── Invoice / credits methods ──────────────────────────────────


class TestGetInvoice(LoopiaTestCase):
    def test_returns_invoice(self):
        self.mock_rpc.getInvoice.return_value = {
            "reference_no": "INV-1",
            "total": 200.0,
            "credits": 0.0,
            "vat": 50.0,
            "to_pay": 250.0,
            "currency": "SEK",
            "expires": "2025-06-01",
            "items": [{"product": "Hosting", "until": "", "fee": 200.0, "discount": 0.0, "items": 1.0, "subtotal": 200.0}],
        }
        inv = self.client.get_invoice("INV-1")
        self.assertEqual(inv.reference_no, "INV-1")
        self.assertEqual(inv.total, 200.0)
        self.assertEqual(len(inv.items), 1)
        self.assertEqual(inv.items[0].product, "Hosting")


class TestGetUnpaidInvoices(LoopiaTestCase):
    def test_returns_list(self):
        self.mock_rpc.getUnpaidInvoices.return_value = [
            {"reference_no": "INV-2", "total": 100.0, "credits": 0.0, "vat": 25.0, "to_pay": 125.0, "currency": "SEK", "expires": "2025-07-01", "items": []},
        ]
        invoices = self.client.get_unpaid_invoices()
        self.assertEqual(len(invoices), 1)
        self.assertEqual(invoices[0].reference_no, "INV-2")

    def test_empty(self):
        self.mock_rpc.getUnpaidInvoices.return_value = []
        self.assertEqual(self.client.get_unpaid_invoices(), [])


class TestPayInvoiceUsingCredits(LoopiaTestCase):
    def test_success(self):
        self.mock_rpc.payInvoiceUsingCredits.return_value = "OK"
        result = self.client.pay_invoice_using_credits("INV-1")
        self.assertEqual(result, "OK")

    def test_insufficient_funds(self):
        self.mock_rpc.payInvoiceUsingCredits.return_value = "INSUFFICIENT_FUNDS"
        with self.assertRaises(LoopiaError) as ctx:
            self.client.pay_invoice_using_credits("INV-1")
        self.assertEqual(ctx.exception.status, "INSUFFICIENT_FUNDS")


class TestGetCreditsAmount(LoopiaTestCase):
    def test_returns_float(self):
        self.mock_rpc.getCreditsAmount.return_value = 500.75
        amount = self.client.get_credits_amount()
        self.assertEqual(amount, 500.75)

    def test_with_customer_number(self):
        self.mock_rpc.getCreditsAmount.return_value = 100.0
        amount = self.client.get_credits_amount(customer_number="C123")
        self.assertEqual(amount, 100.0)


# ── Reseller methods ───────────────────────────────────────────


class TestGetCustomers(LoopiaTestCase):
    def test_returns_list(self):
        self.mock_rpc.getCustomers.return_value = [
            {"company": "Acme", "name": "John", "customer_number": "C1", "account_type": "HOSTING_BUSINESS"},
            {"company": "", "name": "Jane", "customer_number": "C2", "account_type": "LOOPIADOMAIN"},
        ]
        customers = self.client.reseller.get_customers()
        self.assertEqual(len(customers), 2)
        self.assertEqual(customers[0].company, "Acme")
        self.assertEqual(customers[1].name, "Jane")


class TestGetOrderStatus(LoopiaTestCase):
    def test_returns_status(self):
        self.mock_rpc.getOrderStatus.return_value = {
            "order_status": "PROCESSED",
            "customer_number": "C999",
        }
        status = self.client.reseller.get_order_status("REF-1")
        self.assertEqual(status.order_status, "PROCESSED")
        self.assertEqual(status.customer_number, "C999")


class TestCreateNewAccount(LoopiaTestCase):
    def test_success(self):
        self.mock_rpc.createNewAccount.return_value = {
            "status": "OK",
            "order_reference": "ORD-1",
        }
        contact = Contact(firstname="John", lastname="Doe", email="john@example.com")
        result = self.client.reseller.create_new_account("newdomain.com", contact)
        self.assertEqual(result.status, "OK")
        self.assertEqual(result.order_reference, "ORD-1")
        self.mock_rpc.createNewAccount.assert_called_once_with(
            "user@loopiaapi",
            "secret",
            "newdomain.com",
            contact.to_dict(),
            False,
            False,
            False,
            "NO_CONFIG",
            "LOOPIADOMAIN",
            True,
        )


class TestTransferCreditsByCurrency(LoopiaTestCase):
    def test_success(self):
        self.mock_rpc.transferCreditsByCurrency.return_value = "OK"
        result = self.client.reseller.transfer_credits_by_currency("C123", 100.0, "SEK")
        self.assertEqual(result, "OK")
        self.mock_rpc.transferCreditsByCurrency.assert_called_once_with(
            "user@loopiaapi", "secret", "C123", 100.0, "SEK",
        )

    def test_insufficient_funds(self):
        self.mock_rpc.transferCreditsByCurrency.return_value = "INSUFFICIENT_FUNDS"
        with self.assertRaises(LoopiaError):
            self.client.reseller.transfer_credits_by_currency("C123", 999999.0, "SEK")


# ── Error handling ──────────────────────────────────────────────


class TestLoopiaError(unittest.TestCase):
    def test_str(self):
        err = LoopiaError("UNKNOWN_ERROR")
        self.assertEqual(str(err), "UNKNOWN_ERROR")
        self.assertEqual(err.status, "UNKNOWN_ERROR")

    def test_all_statuses(self):
        for status in ["AUTH_ERROR", "DOMAIN_OCCUPIED", "RATE_LIMITED", "BAD_INDATA", "UNKNOWN_ERROR", "INSUFFICIENT_FUNDS"]:
            with self.assertRaises(LoopiaError):
                _check_status(status)


# ── Customer number routing ────────────────────────────────────


class TestCustomerNumberRouting(LoopiaTestCase):
    def test_add_subdomain_with_customer(self):
        self.mock_rpc.addSubdomain.return_value = "OK"
        self.client.add_subdomain("example.com", "www", customer_number="C1")
        self.mock_rpc.addSubdomain.assert_called_once_with(
            "user@loopiaapi", "secret", "C1", "example.com", "www",
        )

    def test_remove_subdomain_with_customer(self):
        self.mock_rpc.removeSubdomain.return_value = "OK"
        self.client.remove_subdomain("example.com", "www", customer_number="C1")
        self.mock_rpc.removeSubdomain.assert_called_once_with(
            "user@loopiaapi", "secret", "C1", "example.com", "www",
        )

    def test_get_subdomains_with_customer(self):
        self.mock_rpc.getSubdomains.return_value = ["@"]
        self.client.get_subdomains("example.com", customer_number="C1")
        self.mock_rpc.getSubdomains.assert_called_once_with(
            "user@loopiaapi", "secret", "C1", "example.com",
        )

    def test_get_zone_records_with_customer(self):
        self.mock_rpc.getZoneRecords.return_value = []
        self.client.get_zone_records("example.com", "@", customer_number="C1")
        self.mock_rpc.getZoneRecords.assert_called_once_with(
            "user@loopiaapi", "secret", "C1", "example.com", "@",
        )

    def test_remove_zone_record_with_customer(self):
        self.mock_rpc.removeZoneRecord.return_value = "OK"
        self.client.remove_zone_record("example.com", "@", 1, customer_number="C1")
        self.mock_rpc.removeZoneRecord.assert_called_once_with(
            "user@loopiaapi", "secret", "C1", "example.com", "@", 1,
        )

    def test_get_domains_with_customer(self):
        self.mock_rpc.getDomains.return_value = []
        self.client.get_domains(customer_number="C1")
        self.mock_rpc.getDomains.assert_called_once_with(
            "user@loopiaapi", "secret", "C1",
        )

    def test_remove_domain_with_customer(self):
        self.mock_rpc.removeDomain.return_value = "OK"
        self.client.remove_domain("example.com", customer_number="C1")
        self.mock_rpc.removeDomain.assert_called_once_with(
            "user@loopiaapi", "secret", "C1", "example.com",
        )

    def test_get_invoice_with_customer(self):
        self.mock_rpc.getInvoice.return_value = {"reference_no": "X", "items": []}
        self.client.get_invoice("X", customer_number="C1")
        self.mock_rpc.getInvoice.assert_called_once_with(
            "user@loopiaapi", "secret", "C1", "X",
        )

    def test_get_unpaid_invoices_with_customer(self):
        self.mock_rpc.getUnpaidInvoices.return_value = []
        self.client.get_unpaid_invoices(customer_number="C1")
        self.mock_rpc.getUnpaidInvoices.assert_called_once_with(
            "user@loopiaapi", "secret", "C1",
        )

    def test_pay_invoice_with_customer(self):
        self.mock_rpc.payInvoiceUsingCredits.return_value = "OK"
        self.client.pay_invoice_using_credits("INV-1", customer_number="C1")
        self.mock_rpc.payInvoiceUsingCredits.assert_called_once_with(
            "user@loopiaapi", "secret", "C1", "INV-1",
        )

    def test_order_domain_with_customer(self):
        self.mock_rpc.orderDomain.return_value = "OK"
        self.client.order_domain("example.com", True, customer_number="C1")
        self.mock_rpc.orderDomain.assert_called_once_with(
            "user@loopiaapi", "secret", "C1", "example.com", True,
        )

    def test_transfer_domain_with_customer(self):
        self.mock_rpc.transferDomain.return_value = "OK"
        self.client.transfer_domain("example.com", "AUTH", customer_number="C1")
        self.mock_rpc.transferDomain.assert_called_once_with(
            "user@loopiaapi", "secret", "C1", "example.com", "AUTH",
        )

    def test_update_dns_servers_with_customer(self):
        self.mock_rpc.updateDNSServers.return_value = "OK"
        self.client.update_dns_servers("example.com", ["ns1.x.com", "ns2.x.com"], customer_number="C1")
        self.mock_rpc.updateDNSServers.assert_called_once_with(
            "user@loopiaapi", "secret", "C1", "example.com", ["ns1.x.com", "ns2.x.com"],
        )

    def test_get_order_status_with_customer(self):
        self.mock_rpc.getOrderStatus.return_value = {"order_status": "PENDING", "customer_number": ""}
        self.client.reseller.get_order_status("REF-1", customer_number="C1")
        self.mock_rpc.getOrderStatus.assert_called_once_with(
            "user@loopiaapi", "secret", "C1", "REF-1",
        )


if __name__ == "__main__":
    unittest.main()

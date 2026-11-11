# Ported from l10n_cz/tests/test_cz_qr.py in Odoo 20.0
# (odoo/odoo@060e7bdebe8e9ea210808f1760fe9c8b8cf1e415, Copyright Odoo S.A., LGPL-3).
# The tests of the QR code values cover the deviation from Odoo 20.0 described in
# models/res_bank.py.
from datetime import timedelta
from unittest.mock import patch

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.addons.ash_cz_qr_payment.models.res_bank import ResPartnerBank


@tagged("post_install_l10n", "post_install", "-at_install")
class TestCZKQRCode(AccountTestInvoicingCommon):
    """Tests the generation of Czech CZK QR-codes on invoices."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.company_data["company"].qr_code = True
        cls.env.ref("base.EUR").active = True
        cls.env.ref("base.CZK").active = True

        cls.acc_czk_iban = cls.env["res.partner.bank"].create(
            {
                "acc_number": "CZ6508000000192000145399",
                "partner_id": cls.company_data["company"].partner_id.id,
                "allow_out_payment": True,
            }
        )

        cls.company_data["default_journal_sale"].invoice_reference_model = "number"
        cls.czk_qr_invoice = cls._create_invoice(
            currency_id=cls.env.ref("base.CZK").id,
            partner_bank_id=cls.acc_czk_iban.id,
            invoice_date_due=fields.Date.today(),
            invoice_line_ids=[
                cls._prepare_invoice_line(price_unit=100),
            ],
        )

    def test_czk_qr_code_generation(self):
        """Check different cases of CZK QR-code generation."""
        self.czk_qr_invoice.qr_code_method = "czk_qr"

        # Using a valid CZK IBAN should work.
        self.czk_qr_invoice._generate_qr_code()

        # Using a non-CZK currency shouldn't work.
        self.czk_qr_invoice.currency_id = self.env.ref("base.EUR")
        with self.assertRaises(UserError):
            self.czk_qr_invoice._generate_qr_code()

        # Restore CZK currency.
        self.czk_qr_invoice.currency_id = self.env.ref("base.CZK")

        # Using a non-IBAN account shouldn't work.
        self.czk_qr_invoice.partner_bank_id = self.env["res.partner.bank"].create(
            {
                "acc_number": "123456789",
                "partner_id": self.company_data["company"].partner_id.id,
                "allow_out_payment": True,
            }
        )

        with self.assertRaises(UserError):
            self.czk_qr_invoice._generate_qr_code()

    def test_czk_qr_code_detection(self):
        """Check automatic detection of the CZK QR-code method."""
        self.czk_qr_invoice._generate_qr_code()

        self.assertEqual(
            self.czk_qr_invoice.qr_code_method,
            "czk_qr",
            "CZK QR-code generator should have been chosen for this invoice.",
        )

    @classmethod
    def _create_vendor_bill(cls, partner_bank, ref, invoice_date_due):
        return cls._create_invoice(
            move_type="in_invoice",
            currency_id=cls.env.ref("base.CZK").id,
            partner_bank_id=partner_bank.id,
            payment_reference="1234567890",
            ref=ref,
            invoice_date_due=invoice_date_due,
            invoice_line_ids=[cls._prepare_invoice_line(price_unit=100)],
            post=True,
        )

    def _capture_qr_vals(self, generate):
        """Return the QR code values computed while calling ``generate``."""
        get_qr_vals = ResPartnerBank._get_qr_vals
        results = []

        def spy(bank, *args, **kwargs):
            results.append(get_qr_vals(bank, *args, **kwargs))
            return results[-1]

        with patch.object(ResPartnerBank, "_get_qr_vals", spy):
            generate()
        self.assertTrue(results)
        return results[-1]

    def _register_payment_qr_vals(self, bills):
        def generate():
            wizard = (
                self.env["account.payment.register"]
                .with_context(active_model="account.move", active_ids=bills.ids)
                .create({})
            )
            self.assertTrue(wizard.qr_code)

        return self._capture_qr_vals(generate)

    def test_czk_qr_vals(self):
        """Customer invoice: the payment reference is the variable symbol and the
        invoice number the message."""
        self.czk_qr_invoice.action_post()
        invoice = self.czk_qr_invoice

        result = self._capture_qr_vals(invoice._generate_qr_code)

        expected = (
            "SPD*1.0*"
            "ACC:CZ6508000000192000145399*"
            f"AM:{invoice.amount_residual}*"
            "CC:CZK*"
            f"DT:{fields.Date.today().strftime('%Y%m%d')}*"
            f"MSG:{invoice.name}*"
            f"RN:{self.acc_czk_iban.acc_holder_name or self.acc_czk_iban.partner_id.name}"  # noqa: E501
            "*PT:IP*"
            f"X-VS:{invoice.payment_reference}*"
        )
        self.assertEqual(result, expected)
        self.assertTrue(invoice.payment_reference.isdigit())

    def test_czk_qr_vals_vendor_bill(self):
        """Vendor bill: the payment reference is the variable symbol and the
        vendor's bill number the message; with the same payment reference on
        several bills, the due date comes from the paid one."""
        vendor_bank = self.env["res.partner.bank"].create(
            {
                "acc_number": "CZ1801000000000123456789",
                "partner_id": self.partner_a.id,
                "allow_out_payment": True,
            }
        )
        today = fields.Date.today()
        self._create_vendor_bill(vendor_bank, "FV-2026-0001", today)
        bill = self._create_vendor_bill(
            vendor_bank, "FV-2026-0002", today + timedelta(days=30)
        )

        result = self._register_payment_qr_vals(bill)

        expected = (
            "SPD*1.0*"
            "ACC:CZ1801000000000123456789*"
            f"AM:{bill.amount_residual}*"
            "CC:CZK*"
            f"DT:{bill.invoice_date_due.strftime('%Y%m%d')}*"
            "MSG:FV-2026-0002*"
            f"RN:{vendor_bank.acc_holder_name or self.partner_a.name}"
            "*PT:IP*"
            "X-VS:1234567890*"
        )
        self.assertEqual(result, expected)

    def test_czk_qr_vals_several_vendor_bills(self):
        """A payment of several bills has no variable symbol and no due date."""
        vendor_bank = self.env["res.partner.bank"].create(
            {
                "acc_number": "CZ1801000000000123456789",
                "partner_id": self.partner_a.id,
                "allow_out_payment": True,
            }
        )
        today = fields.Date.today()
        bills = self._create_vendor_bill(
            vendor_bank, "FV-2026-0001", today
        ) | self._create_vendor_bill(vendor_bank, "FV-2026-0002", today)

        result = self._register_payment_qr_vals(bills)

        self.assertIn("MSG:1234567890*", result)
        self.assertNotIn("X-VS:", result)
        self.assertNotIn("DT:", result)

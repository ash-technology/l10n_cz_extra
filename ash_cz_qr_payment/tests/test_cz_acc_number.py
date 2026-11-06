from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install_l10n", "post_install", "-at_install")
class TestCzAccNumber(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.ref("base.CZK").active = True

    def _create_bank_account(self, acc_number, **vals):
        return self.env["res.partner.bank"].create(
            {
                "acc_number": acc_number,
                "partner_id": self.company_data["company"].partner_id.id,
                **vals,
            }
        )

    def test_cz_acc_number(self):
        # The first two are the examples of the Czech National Bank
        for iban, acc_number in [
            ("CZ6508000000192000145399", "19-2000145399/0800"),
            ("CZ6907101781240000004159", "178124-4159/0710"),
            ("CZ7908000000002000145399", "2000145399/0800"),
        ]:
            with self.subTest(iban=iban):
                bank_account = self._create_bank_account(iban)
                self.assertEqual(bank_account._get_cz_acc_number(), acc_number)
        for acc_number in ["SK3112000000198742637541", "2000145399/0800"]:
            with self.subTest(acc_number=acc_number):
                bank_account = self._create_bank_account(acc_number)
                self.assertFalse(bank_account._get_cz_acc_number())

    def test_report_invoice(self):
        bank = self.env["res.bank"].create({"name": "ČSOB"})
        cz_account = self._create_bank_account(
            "CZ6907101781240000004159", bank_id=bank.id, allow_out_payment=True
        )
        invoice = self._create_invoice(
            currency_id=self.env.ref("base.CZK").id,
            partner_bank_id=cz_account.id,
            invoice_line_ids=[self._prepare_invoice_line(price_unit=100)],
            post=True,
        )
        html = (
            self.env["ir.actions.report"]
            ._render_qweb_html("account.report_invoice", invoice.ids)[0]
            .decode()
        )
        self.assertIn("178124-4159/0710</span> - ČSOB", html)
        self.assertIn("IBAN: <span", html)
        self.assertIn("CZ69 0710 1781 2400 0000 4159", html)

        invoice.partner_bank_id = self._create_bank_account(
            "SK3112000000198742637541", allow_out_payment=True
        )
        html = (
            self.env["ir.actions.report"]
            ._render_qweb_html("account.report_invoice", invoice.ids)[0]
            .decode()
        )
        self.assertIn("SK31 1200 0000 1987 4263 7541", html)
        self.assertNotIn("IBAN: <span", html)

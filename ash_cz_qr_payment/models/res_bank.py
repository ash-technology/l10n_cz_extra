# Backport of the "czk_qr" method of l10n_cz in Odoo 20.0
# (odoo/odoo@060e7bdebe8e9ea210808f1760fe9c8b8cf1e415, Copyright Odoo S.A.,
# LGPL-3), adapted to the Odoo 19.0 field names. It must keep behaving exactly
# like the original, so that migrating to 20.0 only means uninstalling this module.
import re

from odoo import api, models

from odoo.addons.base_iban.models.res_partner_bank import get_iban_part


class ResPartnerBank(models.Model):
    _inherit = "res.partner.bank"

    def _get_qr_vals(
        self,
        qr_method,
        amount,
        currency,
        debtor_partner,
        free_communication,
        structured_communication,
    ):
        if qr_method == "czk_qr":
            invoice = self.env["account.move"].search(
                [
                    *self.env["account.move"]._check_company_domain(self.env.company),
                    "|",
                    ("payment_reference", "=", free_communication),
                    ("name", "=", free_communication),
                ],
                limit=1,
            )

            qr_code_vals = {
                # Account Number
                "ACC": self.sanitized_acc_number,
                # Amount
                "AM": amount,
                # Currency
                "CC": currency.name,
                # Due Date
                "DT": invoice.invoice_date_due.strftime("%Y%m%d")
                if invoice and invoice.invoice_date_due
                else "",
                # Message for Recipient
                "MSG": free_communication[:60] if free_communication else "",
                # Recipient Name
                "RN": (self.acc_holder_name or self.partner_id.name)[:35],
                # Payment Type
                "PT": "IP",
                # Variable Symbol
                "X-VS": re.sub(r"\D+", "", invoice.name)
                if invoice and invoice.name
                else "",
            }

            qr_code_data = "*".join(
                f"{key}:{value}" for key, value in qr_code_vals.items() if value
            )

            return f"SPD*1.0*{qr_code_data}*"
        return super()._get_qr_vals(
            qr_method,
            amount,
            currency,
            debtor_partner,
            free_communication,
            structured_communication,
        )

    def _get_qr_code_generation_params(
        self,
        qr_method,
        amount,
        currency,
        debtor_partner,
        free_communication,
        structured_communication,
    ):
        if qr_method == "czk_qr":
            return {
                "barcode_type": "QR",
                "quiet": 0,
                "width": 128,
                "height": 128,
                "value": self._get_qr_vals(
                    qr_method,
                    amount,
                    currency,
                    debtor_partner,
                    free_communication,
                    structured_communication,
                ),
            }
        return super()._get_qr_code_generation_params(
            qr_method,
            amount,
            currency,
            debtor_partner,
            free_communication,
            structured_communication,
        )

    def _get_error_messages_for_qr(self, qr_method, debtor_partner, currency):
        if qr_method == "czk_qr":
            error_messages = []
            if currency.id != self.env.ref("base.CZK").id:
                error_messages.append(
                    self.env._(
                        "The bank account currency must be CZK to generate the QR code."
                    )
                )
            if self.acc_type != "iban":
                error_messages.append(
                    self.env._(
                        "The bank account type must be IBAN to generate the QR code."
                    )
                )
            if not self.sanitized_acc_number:
                error_messages.append(
                    self.env._(
                        "An IBAN account number is required to generate the QR code."
                    )
                )
            if len(error_messages) > 0:
                return "\r\n".join(error_messages)
            return None
        return super()._get_error_messages_for_qr(qr_method, debtor_partner, currency)

    @api.model
    def _get_available_qr_methods(self):
        rslt = super()._get_available_qr_methods()
        rslt.append(("czk_qr", self.env._("CZK QR"), 50))
        return rslt

    # Not part of Odoo 20.0: the Czech account number printed on the invoice
    # (views/report_invoice.xml).
    def _get_cz_acc_number(self):
        # National format of a Czech IBAN (CNB decree 169/2011, art. 4 and 5):
        # [prefix-]number/bank code. The "branch" part of the Odoo IBAN template
        # is the prefix; leading zeros of the prefix and the number have no
        # significance.
        if self.acc_type != "iban" or not self.sanitized_acc_number.startswith("CZ"):
            return False
        prefix = get_iban_part(self.acc_number, "branch").lstrip("0")
        number = get_iban_part(self.acc_number, "account").lstrip("0")
        bank_code = get_iban_part(self.acc_number, "bank")
        return f"{prefix}-{number}/{bank_code}" if prefix else f"{number}/{bank_code}"
